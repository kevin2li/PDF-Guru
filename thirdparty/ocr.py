import argparse
import glob
import os
import re
import shutil
import traceback
from pathlib import Path

import cv2
import fitz
import numpy as np
from paddleocr import PaddleOCR, PPStructure, draw_ocr
from PIL import Image
from tqdm import tqdm


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
    
def ppstructure_analysis(input_path: str):
    img = cv2.imread(input_path)
    structure_engine = PPStructure(table=False, ocr=False, show_log=False)
    result = structure_engine(img)
    return result

def parse_range(page_range: str, is_multiple: bool = False):
    # e.g.: "1-3,5-6,7-10", "1,4-5"
    page_range = page_range.strip()
    parts = page_range.split(",")
    roi_indices = []
    for part in parts:
        out = list(map(int, part.split("-")))
        if len(out) == 2:
            roi_indices.append(list(range(out[0]-1, out[1])))
        elif len(out) == 1:
            roi_indices.append([out[0]-1])
    if is_multiple:
        return roi_indices
    result = [j for i in roi_indices for j in i]
    return result

def center_y(elem):
    return (elem[0][0][1]+elem[0][3][1])/2

def write_ocr_result(ocr_results, output_path: str, offset: int = 5):
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
    with open(output_path, "w", encoding="utf-8") as f:
        for row in results:
            line = ""
            for item in row:
                pos, (text, prob) = item
                line += f"{text} "
            line = line.rstrip()
            f.write(f"{line}\n")

def ocr_from_image(input_path: str, lang: str = 'ch', output_path: str = None, offset: float = 5., use_double_columns: bool = False, show_log: bool = False):
    p = Path(input_path)
    if output_path is None:
        output_dir = p.parent / "ocr_result"
    else:
        output_dir = Path(output_path)
    output_dir.mkdir(parents=True, exist_ok=True)

    ocr_engine = PaddleOCR(use_angle_cls=True, lang=lang, show_log=show_log) # need to run only once to download and load model into memory
    img = cv2.imread(input_path)
    result = None
    if use_double_columns:
        height, width = img.shape[:2]
        mid = width / 2
        left_img = img[:, :int(mid)]
        right_img = img[:, int(mid):]
        left_result = ocr_engine.ocr(left_img, cls=False)[0]
        right_result = ocr_engine.ocr(right_img, cls=False)[0]
        result = left_result + right_result
    else:
        result = ocr_engine.ocr(img, cls=False)[0]

    # 保存识别结果文本
    text_output_path = str(output_dir / f"{p.stem}-ocr.txt")
    write_ocr_result(result, text_output_path, offset)

def ocr_from_pdf(doc_path: str, page_range: str = 'all', lang: str = 'ch', output_path: str = None, offset: float = 5., use_double_columns: bool = False, show_log: bool = False):
    doc: fitz.Document = fitz.open(doc_path)
    p = Path(doc_path)
    if output_path is None:
        output_path = p.parent / f"{p.stem}_ocr_result"
    else:
        output_path = Path(output_path)
    output_path.mkdir(parents=True, exist_ok=True)
    if page_range in ["all", ""]:
        roi_indices = list(range(len(doc)))
    else:
        roi_indices = parse_range(page_range)
    ocr_engine = PaddleOCR(use_angle_cls=True, lang=lang, show_log=show_log) # need to run only once to download and load model into memory
    for page_index in tqdm(roi_indices): # iterate over pdf pages
        page = doc[page_index] # get the page
        pix: fitz.Pixmap = page.get_pixmap()  # render page to an image
        img = np.frombuffer(pix.samples, dtype=np.uint8).reshape((pix.height, pix.width, pix.n))
        result = None
        if use_double_columns:
            height, width = img.shape[:2]
            mid = width / 2
            left_img = img[:, :int(mid)]
            right_img = img[:, int(mid):]
            left_result = ocr_engine.ocr(left_img, cls=False)[0]
            right_result = ocr_engine.ocr(right_img, cls=False)[0]
            result = left_result + right_result
        else:
            result = ocr_engine.ocr(img, cls=False)[0]
        write_ocr_result(result, output_path / f"{page_index}-ocr.txt", offset)

    path_list = sorted(list(filter(lambda x: x.endswith(".txt"), os.listdir(output_path))), key=lambda x: int(re.search("(\d+)", x).group(1)))
    merged_path = output_path / "合并.txt"
    with open(merged_path, "a", encoding="utf-8") as f:
        for path in path_list:
            abs_path = os.path.join(output_path, path)
            with open(abs_path, "r", encoding="utf-8") as f2:
                for line in f2:
                    f.write(line)

def extract_title(input_path: str, lang: str = 'ch', use_double_columns: bool = False) -> list:
    # TODO: 存在标题识别不全bug
    ocr_engine = PaddleOCR(use_angle_cls=True, lang=lang, show_log=False) # need to run only once to download and load model into memory
    img = cv2.imread(input_path)
    result = ppstructure_analysis(input_path)
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

def add_toc_from_ocr(doc_path: str, lang: str='ch', use_double_columns: bool = False, output_path: str = None):
    doc: fitz.Document = fitz.open(doc_path)
    p = Path(doc_path)
    tmp_dir = p.parent / 'tmp'
    tmp_dir.mkdir(parents=True, exist_ok=True)
    
    toc = []
    for page in tqdm(doc, total=doc.page_count):
        pix: fitz.Pixmap = page.get_pixmap()  # render page to an image
        savepath = str(tmp_dir / f"page-{page.number+1}.png")
        # pix.save(savepath)  # store image as a PNG
        pix.pil_save(savepath, quality=100, dpi=(1800,1800))
        result = extract_title(savepath, lang, use_double_columns)
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

    # 设置目录
    doc.set_toc(toc)
    if output_path is None:
        output_path = str(p.parent / f"{p.stem}-toc.pdf")
    doc.save(output_path)
    shutil.rmtree(tmp_dir)

def main():
    parser = argparse.ArgumentParser()
    sub_parsers = parser.add_subparsers()
    ocr_parser = sub_parsers.add_parser("ocr", help="ocr识别")
    ocr_parser.add_argument("input_path", type=str, help="pdf文件路径")
    ocr_parser.add_argument("-o", "--output", type=str, help="输出文件路径")
    ocr_parser.add_argument("--lang", type=str, default="ch", choices=['ch', 'en'], help="识别语言")
    ocr_parser.add_argument("--range", type=str, default="", help="页码范围")
    ocr_parser.add_argument("--use-double-column", action="store_true", help="是否双栏")
    ocr_parser.add_argument("--offset", type=int, default=5, help="识别为同一行的偏移量")
    ocr_parser.set_defaults(which='ocr')

    bookmark_parser = sub_parsers.add_parser("bookmark", help="书签识别")
    bookmark_parser.set_defaults(which='bookmark')

    extract_parser = sub_parsers.add_parser("extract", help="图片、表格提取等")
    extract_parser.set_defaults(which='extract')

    args = parser.parse_args()
    if args.which == "ocr":
        p = Path(args.input_path)
        if p.suffix in [".png", '.jpg', ".jpeg"]:
            ocr_from_image(args.input_path, args.lang, args.output, args.offset, args.use_double_column)
        elif p.suffix in ['.pdf']:
            ocr_from_pdf(args.input_path, args.range, args.lang, args.output, args.offset, args.use_double_column)
        else:
            raise ValueError("不支持的文件格式")


if __name__ == "__main__":
    main()
    # input_path = "C:\\Users\\kevin\\Downloads\\Snipaste_2023-06-29_09-51-08.png"
    # lang = 'ch'
    # output_path = "output"
    # ocr_from_image(input_path, lang)