import argparse
import glob
import json
import logging
import os
import re
import shutil
import traceback
from pathlib import Path

import cv2
import fitz
import matplotlib.pyplot as plt
import numpy as np
from paddleocr import PaddleOCR, PPStructure, draw_ocr, save_structure_res
from paddleocr.ppstructure.recovery.recovery_to_doc import (
    convert_info_docx, sorted_layout_boxes)
from PIL import Image
from tqdm import tqdm

ocr_engine_ch = PaddleOCR(use_angle_cls=True, lang='ch', show_log=False) # need to run only once to download and load model into memory
ocr_engine_en = PaddleOCR(use_angle_cls=True, lang='en', show_log=False) # need to run only once to download and load model into memory
structure_engine = PPStructure(table=False, ocr=False, show_log=False)

cmd_output_path = "cmd_output.json"

def init_logger(name: str, logpath: str):
    logger = logging.getLogger(name)
    logger.setLevel(logging.DEBUG)
    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    fh = logging.FileHandler(logpath)
    fh.setLevel(logging.DEBUG)
    fh.setFormatter(formatter)
    logger.addHandler(fh)
    return logger

logger = init_logger(name="pdf guru: ocr_logger", logpath="pdf_guru-ocr.log")

def dump_json(path, obj):
    with open(path, "w", encoding="utf-8") as f:
        json.dump(obj, f, ensure_ascii=False)

def batch_process(func):
    def wrapper(*args, **kwargs):
        logger.debug(args)
        logger.debug(kwargs)
        input_path = kwargs['input_path']
        if "*" in input_path:
            path_list = glob.glob(input_path)
            logger.debug(f"path_list length: {len(path_list) if path_list else 0}")
            if path_list:
                for path in path_list:
                    kwargs["input_path"] = path
                    func(*args, **kwargs)
        else:
            func(*args, **kwargs)
        func(*args, **kwargs)
    return wrapper

def plot_roi_region(img, ppstructure_result, output_path: str, type: str = 'title'):
    if isinstance(img, str):
        img = cv2.imread(img)
    elif isinstance(img, np.ndarray):
        pass
    else:
        raise ValueError("不支持的输入类型")
    logger.debug(img.shape)
    for item in ppstructure_result:
        if item['type'] == type:
            logger.debug("found!")
            x1, y1, x2, y2 = item['bbox']
            cv2.rectangle(img, (x1, y1), (x2, y2), color=(255, 0, 0), thickness=2)
    logger.debug(f"output_path: {output_path}")
    plt.imsave(output_path, img)
    # cv2.imwrite(output_path, img) # 保存中文路径失败

def title_preprocess(title: str):
    """提取标题层级和标题内容
    """
    try:
        title = title.rstrip()
        res = {}
        # 优先根据缩进匹配
        if title.startswith("\t"):
            m = re.match("(\t*)\s*(.+)", title)
            res['text'] = f"{m.group(2)}".rstrip()
            res['level'] = len(m.group(1))+1
            return res

        # 匹配：1.1.1 标题
        m = re.match("\s*((\d+\.?)+)\s*(.+)", title)
        if m is not None:
            res['text'] = f"{m.group(1)} {m.group(3)}"
            res['level'] = len([v for v in m.group(1).split(".") if v])
            return res
        
        # 匹配：第1章 标题
        m = re.match("\s*(第.+[章|编])\s*(.+)", title)
        if m is not None:
            res['text'] = f"{m.group(1)} {m.group(2)}"
            res['level'] = 1
            return res

        # 匹配：第1节 标题
        m = re.match("\s*(第.+节)\s*(.+)", title)
        if m is not None:
            res['text'] = f"{m.group(1)} {m.group(2)}"
            res['level'] = 2
            return res
        
        # 无匹配
        res['text'] = title
        res['level'] = 1
        return res
    except:
        traceback.print_exc()
        return {'level': 1, "text": title}
    
def parse_range(page_range: str, page_count: int, is_multi_range: bool = False, is_reverse: bool = False, is_unique: bool = True):
    # e.g.: "1-3,5-6,7-10", "1,4-5", "3-N", "even", "odd"
    page_range = page_range.strip()
    if page_range in ["all", ""]:
        roi_indices = list(range(page_count))
        return roi_indices
    if page_range == "even":
        roi_indices = list(range(0, page_count, 2))
        return roi_indices
    if page_range == "odd":
        roi_indices = list(range(1, page_count, 2))
        return roi_indices
    
    roi_indices = []
    parts = page_range.split(",")
    neg_count = sum([p.startswith("!") for p in parts])
    pos_count = len(parts) - neg_count
    if neg_count > 0 and pos_count > 0:
        raise ValueError("页码格式错误：不能同时使用正向选择和反向选择语法")
    if pos_count > 0:
        for part in parts:
            part = part.strip()
            if re.match("^!?(\d+|N)(\-(\d+|N))?$", part) is None:
                raise ValueError("页码格式错误!")
            out = part.split("-")
            if len(out) == 1:
                if out[0] == "N":
                    roi_indices.append([page_count-1])
                else:
                    roi_indices.append([int(out[0])-1])
            elif len(out) == 2:
                if out[1] == "N":
                    roi_indices.append(list(range(int(out[0])-1, page_count)))
                else:
                    roi_indices.append(list(range(int(out[0])-1, int(out[1]))))
        if is_multi_range:
            return roi_indices
        roi_indices = [i for v in roi_indices for i in v]
        if is_unique:
            roi_indices = list(set(roi_indices))
            roi_indices.sort()
    if neg_count > 0:
        for part in parts:
            part = part.strip()
            if re.match("^!?(\d+|N)(\-(\d+|N))?$", part) is None:
                raise ValueError("页码格式错误!")
            out = part[1:].split("-")
            if len(out) == 1:
                roi_indices.append([int(out[0])-1])
            elif len(out) == 2:
                if out[1] == "N":
                    roi_indices.append(list(range(int(out[0])-1, page_count)))
                else:
                    roi_indices.append(list(range(int(out[0])-1, int(out[1]))))
        if is_multi_range:
            return roi_indices
        roi_indices = [i for v in roi_indices for i in v]
        if is_unique:
            roi_indices = list(set(range(page_count)) - set(roi_indices))
            roi_indices.sort()
    if is_reverse:
        roi_indices = list(set(range(page_count)) - set(roi_indices))
        roi_indices.sort()
    return roi_indices


def center_y(elem):
    return (elem[0][0][1]+elem[0][3][1])/2

def write_ocr_result(ocr_results, output_path: str, offset: int = 5, mode: str = "w", encoding: str = "utf-8"):
    # 按照 y中点 坐标排序
    sorted_by_y = sorted(ocr_results, key=lambda x: center_y(x))
    results = []
    temp_row = [sorted_by_y[0]]
    for i in range(1, len(sorted_by_y)):
        # 如果和前一个元素的 y 坐标差值小于偏移量，则视为同一行
        if abs(center_y(sorted_by_y[i]) - center_y(sorted_by_y[i-1])) < offset:
            temp_row.append(sorted_by_y[i])
        else:
            # 按照 x 坐标排序，将同一行的元素按照 x 坐标排序
            temp_row = sorted(temp_row, key=lambda x: x[0][0])
            # 将同一行的元素添加到结果列表中
            results.append(temp_row)
            temp_row = [sorted_by_y[i]]
    # 将最后一行的元素添加到结果列表中
    temp_row = sorted(temp_row, key=lambda x: x[0][0])
    results.append(temp_row)
    with open(output_path, mode=mode, encoding=encoding) as f:
        for row in results:
            line = ""
            for item in row:
                pos, (text, prob) = item
                line += f"{text} "
            line = line.rstrip()
            f.write(f"{line}\n")

@batch_process
def ocr_from_image(input_path: str, lang: str = 'ch', output_path: str = None, offset: float = 5., use_double_columns: bool = False, show_log: bool = False):
    try:
        p = Path(input_path)
        if output_path is None:
            output_dir = p.parent / f"{p.stem}-OCR识别"
        else:
            output_dir = Path(output_path)
        output_dir.mkdir(parents=True, exist_ok=True)
        text_output_path = str(output_dir / f"{p.stem}-ocr.txt")
        if lang == 'ch':
            ocr_engine = ocr_engine_ch
        elif lang == 'en':
            ocr_engine = ocr_engine_en
        else:
            raise ValueError("不支持的语言")
        img = cv2.imdecode(np.fromfile(input_path, dtype=np.uint8), cv2.IMREAD_UNCHANGED)[..., :3]
        result = None
        if use_double_columns:
            height, width = img.shape[:2]
            mid = width / 2
            left_img = img[:, :int(mid)]
            right_img = img[:, int(mid):]
            left_result = ocr_engine.ocr(left_img, cls=False)[0]
            right_result = ocr_engine.ocr(right_img, cls=False)[0]
            write_ocr_result(left_result, text_output_path, offset)
            write_ocr_result(right_result, text_output_path, offset, mode="a")
        else:
            result = ocr_engine.ocr(input_path, cls=False)[0]
            write_ocr_result(result, text_output_path, offset)
        dump_json(cmd_output_path, {"status": "success", "message": ""})
    except:
        logger.error(traceback.format_exc())
        dump_json(cmd_output_path, {"status": "error", "message": traceback.format_exc()})

@batch_process
def ocr_from_pdf(input_path: str, page_range: str = 'all', lang: str = 'ch', output_path: str = None, offset: float = 5., use_double_columns: bool = False):
    try:
        doc: fitz.Document = fitz.open(input_path)
        p = Path(input_path)
        if output_path is None:
            output_path = p.parent / f"{p.stem}-OCR识别"
            if not output_path.exists():
                output_path.mkdir(parents=True, exist_ok=True)
            else:
                logger.warning(f"文件夹 {output_path} 已存在，将被删除")
                shutil.rmtree(output_path)
                output_path.mkdir(parents=True, exist_ok=True)
        else:
            output_path = Path(output_path)
            output_path.mkdir(parents=True, exist_ok=True)
        roi_indices = parse_range(page_range, doc.page_count)
        if lang == 'ch':
            ocr_engine = ocr_engine_ch
        elif lang == 'en':
            ocr_engine = ocr_engine_en
        else:
            raise ValueError("不支持的语言")
        dpi = 300
        for page_index in tqdm(roi_indices):
            page = doc[page_index]
            pix = page.get_pixmap(matrix=fitz.Matrix(dpi/72, dpi/72))
            img = np.frombuffer(pix.samples, dtype=np.uint8).reshape((pix.height, pix.width, pix.n))
            cur_output_path = output_path / f"{page_index+1}-OCR.txt"
            result = None
            if use_double_columns:
                height, width = img.shape[:2]
                mid = width / 2
                left_img = img[:, :int(mid)]
                right_img = img[:, int(mid):]
                left_result = ocr_engine.ocr(left_img, cls=False)[0]
                right_result = ocr_engine.ocr(right_img, cls=False)[0]
                write_ocr_result(left_result, cur_output_path, offset)
                write_ocr_result(right_result, cur_output_path, offset, mode="a")
            else:
                result = ocr_engine.ocr(img, cls=False)[0]
                write_ocr_result(result, cur_output_path, offset)
        path_list = sorted(list(filter(lambda x: x.endswith(".txt"), os.listdir(output_path))), key=lambda x: int(re.search("(\d+)", x).group(1)))
        merged_path = output_path / "合并.txt"
        with open(merged_path, "a", encoding="utf-8") as f:
            for path in path_list:
                abs_path = os.path.join(output_path, path)
                with open(abs_path, "r", encoding="utf-8") as f2:
                    for line in f2:
                        f.write(line)
            dump_json(cmd_output_path, {"status": "success", "message": ""})
    except:
        logger.error(traceback.format_exc())
        dump_json(cmd_output_path, {"status": "error", "message": traceback.format_exc()})

def extract_title(input_path: str, lang: str = 'ch', use_double_columns: bool = False, show_path: str = None) -> list:
    # TODO: 存在标题识别不全bug
    if lang == 'ch':
        ocr_engine = ocr_engine_ch
    elif lang == 'en':
        ocr_engine = ocr_engine_en
    else:
        raise ValueError("不支持的语言")
    if isinstance(input_path, str):
        img = cv2.imread(input_path)
    elif isinstance(input_path, np.ndarray):
        img = input_path
    else:
        raise ValueError("不支持的输入类型")
    result = structure_engine(img)
    if show_path is not None:
        plot_roi_region(img=img, ppstructure_result=result, output_path=show_path, type="title")
    title_items = [v for v in result if v['type']=='title']       # 提取title项
    title_items = sorted(title_items, key=lambda x: x['bbox'][1]) # 从上往下排序
    if use_double_columns:
        height, width = img.shape[:2]
        mid = width / 2
        left_title_items = [v for v in title_items if v['bbox'][2]<mid]
        right_title_items = [v for v in title_items if v['bbox'][2]>=mid]
        left_title_items = sorted(left_title_items, key=lambda x: x['bbox'][1]) # 从上往下排序
        right_title_items = sorted(right_title_items, key=lambda x: x['bbox'][1]) # 从上往下排序
        title_items = left_title_items + right_title_items
    x_delta = 10
    y_delta = 5
    out = []
    for item in title_items:
        x1, y1, x2, y2 = item['bbox']
        result = ocr_engine.ocr(img[y1-y_delta: y2+y_delta, x1-x_delta: x2+x_delta], cls=False)
        for idx in range(len(result)):
            res = result[idx]
            for line in res:
                pos, (title, prob) = line
                new_pos = []
                for p in pos:
                    new_pos.append([p[0]+x1-x_delta, p[1]+y1-y_delta])
                out.append([new_pos, (title, prob)])
    return out

def add_toc_from_ocr(input_path: str, lang: str='ch', use_double_columns: bool = False, page_range: str = "all", output_path: str = None):
    try:
        doc: fitz.Document = fitz.open(input_path)
        p = Path(input_path)
        tmp_dir = p.parent / 'temp'
        tmp_dir.mkdir(parents=True, exist_ok=True)
        
        toc = []
        dpi = 300
        roi_indices = parse_range(page_range, doc.page_count)
        for page_index in tqdm(roi_indices):
            page = doc[page_index]
            pix = page.get_pixmap(matrix=fitz.Matrix(dpi/72, dpi/72))
            show_path = str(tmp_dir / f"{page_index+1}.png")
            img = np.frombuffer(buffer=pix.samples, dtype=np.uint8).reshape((pix.height, pix.width, -1))
            result = extract_title(img, lang, use_double_columns, show_path=show_path)
            for item in result:
                pos, (title, prob) = item
                # 书签格式：[|v|, title, page [, dest]]  (层级，标题，页码，高度)
                res = title_preprocess(title)
                level, title = res['level'], res['text']
                height = pos[0][1] # 左上角点的y坐标
                toc.append([level, title, page.number+1, height])
        # 校正层级
        levels = [v[0] for v in toc]
        diff = np.diff(levels)
        indices = np.where(diff>1)[0]
        for idx in indices:
            toc[idx][0] = toc[idx+1][0]
        logger.debug(toc)
        # 设置目录
        doc.set_toc(toc)
        if output_path is None:
            output_path = str(p.parent / f"{p.stem}-OCR生成目录版.pdf")
        doc.save(output_path)
        shutil.rmtree(tmp_dir)
        dump_json(cmd_output_path, {"status": "success", "message": ""})
    except:
        p = Path(input_path)
        toc_output_path = str(p.parent / f"{p.stem}-OCR识别目录.txt")
        with open(toc_output_path, "w", encoding='utf-8') as f:
            for line in toc:
                indent = (line[0]-1)*"\t"
                f.writelines(f"{indent}{line[1]} {line[2]}\n")
        logger.error(traceback.format_exc())
        dump_json(cmd_output_path, {"status": "error", "message": f"请在'{toc_output_path}'中查看目录识别结果！\n" + traceback.format_exc()})

def extract_item_from_pdf(doc_path: str, page_range: str = 'all', type: str = "figure", output_dir: str = None):
    """
    suupported types: figure, table, equation, title, text
    """
    try:
        doc: fitz.Document = fitz.open(doc_path)
        p = Path(doc_path)
        tmp_dir = p.parent / 'tmp'
        tmp_dir.mkdir(parents=True, exist_ok=True)
        if output_dir is None:
            output_dir = p.parent / type
        else:
            output_dir = Path(output_dir) / type
        output_dir.mkdir(parents=True, exist_ok=True)
        roi_indices = parse_range(page_range, doc.page_count)
        dpi = 300
        for page_index in tqdm(roi_indices, total=len(roi_indices)):
            page = doc[page_index]
            pix = page.get_pixmap(matrix=fitz.Matrix(dpi/72, dpi/72))
            img = np.frombuffer(buffer=pix.samples, dtype=np.uint8).reshape((pix.height, pix.width, -1))
            result = structure_engine(img)
            result = [v for v in result if v['type']==type]

            idx = 1
            for item in result:
                im_show = Image.fromarray(item['img'])
                im_show.save(str(output_dir / f"page-{page.number+1}-{type}-{idx}.png"))
                idx += 1
        dump_json(cmd_output_path, {"status": "success", "message": ""})
    except:
        logger.error(traceback.format_exc())
        dump_json(cmd_output_path, {"status": "error", "message": traceback.format_exc()})

def convert_pdf2docx(doc_path: str, lang: str = "ch", dpi: int = 300, page_range: str = "all", output_path: str = None):
    try:
        doc: fitz.Document = fitz.open(doc_path)
        table_engine = PPStructure(recovery=True, lang=lang)
        roi_indicies = parse_range(page_range, doc.page_count)
        p = Path(doc_path)
        if output_path is None:
            output_dir = p.parent / "docx"
            output_dir.mkdir(parents=True, exist_ok=True)
        else:
            output_dir = Path(output_path)
            output_dir.mkdir(parents=True, exist_ok=True)
        for page_index in roi_indicies:
            page = doc[page_index]
            pix = page.get_pixmap(matrix=fitz.Matrix(dpi/72, dpi/72))
            img = np.frombuffer(buffer=pix.samples, dtype=np.uint8).reshape((pix.height, pix.width, -1))
            result = table_engine(img)
            h, w, _ = img.shape
            res = sorted_layout_boxes(result, w)
            convert_info_docx(img, res, output_dir, f"{p.stem}-{page_index+1}")
    except:
        logger.error(traceback.format_exc())
        dump_json(cmd_output_path, {"status": "error", "message": traceback.format_exc()})

def main():
    parser = argparse.ArgumentParser()
    sub_parsers = parser.add_subparsers()
    
    # OCR识别
    ocr_parser = sub_parsers.add_parser("ocr", help="ocr识别")
    ocr_parser.set_defaults(which='ocr')
    ocr_parser.add_argument("input_path", type=str, help="输入文件路径")
    ocr_parser.add_argument("-o", "--output", type=str, help="输出文件路径")
    ocr_parser.add_argument("--lang", type=str, default="ch", choices=['ch', 'en'], help="识别语言")
    ocr_parser.add_argument("--range", type=str, default="", help="页码范围")
    ocr_parser.add_argument("--use-double-column", action="store_true", help="是否双栏")
    ocr_parser.add_argument("--offset", type=int, default=5, help="识别为同一行的偏移量")

    # 书签识别
    bookmark_parser = sub_parsers.add_parser("bookmark", help="书签识别")
    bookmark_parser.set_defaults(which='bookmark')
    bookmark_parser.add_argument("input_path", type=str, help="输入文件路径")
    bookmark_parser.add_argument("-l", "--lang", type=str, default="ch", choices=['ch', 'en', 'fr', 'german', 'it', 'japan', 'korean', 'ru', 'chinese_cht'], dest="lang", help="pdf语言")
    bookmark_parser.add_argument("-d", "--double-columns", action="store_true", dest='use_double_column', default=False, help="是否双栏")
    bookmark_parser.add_argument("-r", "--range", type=str, default="all", dest="page_range", help="指定页面范围,例如: '1-3,7-19'")
    bookmark_parser.add_argument("-o", "--output", type=str, default=None, dest="output_path", help="结果保存路径")

    # 信息提取
    extract_parser = sub_parsers.add_parser("extract", help="图片、表格提取等")
    extract_parser.set_defaults(which='extract')
    extract_parser.add_argument("input_path", type=str, help="输入文件路径")
    extract_parser.add_argument("--type", type=str, default="figure", choices=['figure', 'table', 'equation', 'title', 'text'], help="提取类型")
    extract_parser.add_argument("--range", type=str, default="all", dest="page_range", help="指定页面范围,例如: '1-3,7-19'")
    extract_parser.add_argument("-o", "--output", type=str, default=None, dest="output_dir", help="结果保存路径")

    args = parser.parse_args()
    logger.debug(args)
    if args.which == "ocr":
        p = Path(args.input_path)
        if p.suffix in [".png", '.jpg', ".jpeg"]:
            ocr_from_image(input_path=args.input_path, lang=args.lang, output_path=args.output, offset=args.offset, use_double_columns=args.use_double_column)
        elif p.suffix in ['.pdf']:
            ocr_from_pdf(input_path=args.input_path, page_range=args.range, lang=args.lang, output_path=args.output, offset=args.offset, use_double_columns=args.use_double_column)
        else:
            raise ValueError("不支持的文件格式")
    elif args.which == "bookmark":
        add_toc_from_ocr(input_path=args.input_path, lang=args.lang, use_double_columns=args.use_double_column, page_range=args.page_range, output_path=args.output_path)
    elif args.which == "extract":
        extract_item_from_pdf(doc_path=args.input_path, page_range=args.page_range, type=args.type, output_dir=args.output)

if __name__ == "__main__":
    # main()
    convert_pdf2docx(r"C:\Users\kevin\Desktop\书签测试\计算机网络-目录_提取.pdf")