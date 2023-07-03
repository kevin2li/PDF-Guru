import argparse
import json
import re
import glob
import traceback
from pathlib import Path
from typing import List, Tuple, Union

import fitz
from loguru import logger
from PIL import Image, ImageChops, ImageDraw, ImageEnhance, ImageFont, ImageOps
from reportlab.lib import units
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.pdfgen import canvas

pdfmetrics.registerFont(TTFont('msyh','msyh.ttc'))
pdfmetrics.registerFont(TTFont('simkai','simkai.ttf'))

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

def range_compress(arr):
    if not arr:
        return []
    
    result = []
    start = end = arr[0]
    for i in range(1, len(arr)):
        if arr[i] == end + 1:
            end = arr[i]
        else:
            result.append([start, end])
            start = end = arr[i]
    result.append([start, end])
    return result

def slice_pdf(doc_path: str, page_range: str = "all", output_path: str = None, is_reverse: bool = False):
    try:
        doc: fitz.Document = fitz.open(doc_path)
        p = Path(doc_path)
        if output_path is None:
            output_dir = p.parent
        roi_indices = parse_range(page_range, doc.page_count, is_reverse=is_reverse)
        tmp_doc: fitz.Document = fitz.open()
        parts = range_compress(roi_indices)
        for part in parts:
            tmp_doc.insert_pdf(doc, from_page=part[0], to_page=part[1])
        tmp_doc.save(str(output_dir / f"{p.stem}-切片.pdf"))
    except:
        logger.error(f"roi_indices: {roi_indices}")
        raise ValueError(traceback.format_exc())

def split_pdf_by_chunk(doc_path: str, chunk_size: int, output_path: str = None):
    try:
        doc: fitz.Document = fitz.open(doc_path)
        p = Path(doc_path)
        if output_path is None:
            output_dir = p.parent / "PDF拆分-分块"
            output_dir.mkdir(parents=True, exist_ok=True)
        else:
            output_dir = Path(output_path)
            output_dir.mkdir(parents=True, exist_ok=True)
        for i in range(0, doc.page_count, chunk_size):
            savepath = str(output_dir / f"{p.stem}-{i+1}-{min(i+chunk_size, doc.page_count)}.pdf")
            tmp_doc:fitz.Document = fitz.open()
            tmp_doc.insert_pdf(doc, from_page=i, to_page=min(i+chunk_size, doc.page_count)-1)
            tmp_doc.save(savepath)
    except:
        raise ValueError(traceback.format_exc())

def split_pdf_by_page(doc_path: str, page_range: str = "all", output_path: str = None):
    try:
        doc: fitz.Document = fitz.open(doc_path)
        p = Path(doc_path)
        indices_list = parse_range(page_range, doc.page_count, is_multi_range=True)
        if output_path is None:
            output_dir = p.parent / "PDF拆分-自定义范围"
            output_dir.mkdir(parents=True, exist_ok=True)
        else:
            output_dir = Path(output_path)
            output_dir.mkdir(parents=True, exist_ok=True)
        for i, indices in enumerate(indices_list):
            tmp_doc: fitz.Document = fitz.open()
            parts = range_compress(indices)
            for part in parts:
                tmp_doc.insert_pdf(doc, from_page=part[0], to_page=part[1])
            tmp_doc.save(str(output_dir / f"{p.stem}-part{i}.pdf"))
    except:
        raise ValueError(traceback.format_exc())

def split_pdf_by_toc(doc_path: str, level: int = 1, output_path: str = None):
    try:
        doc: fitz.Document = fitz.open(doc_path)
        p = Path(doc_path)
        toc = doc.get_toc(simple=True)
        if output_path is None:
            output_dir = p.parent / "PDF拆分-目录"
            output_dir.mkdir(parents=True, exist_ok=True)
        else:
            output_dir = Path(output_path)
            output_dir.mkdir(parents=True, exist_ok=True)
        roi_toc = [[i, p] for i, p in enumerate(toc) if p[0] == level]
        begin, end = 0, 0
        for i, p in enumerate(roi_toc):
            # p: [index, [level, title, page_index]
            begin, end = None, None
            cur_idx, next_idx = 0, 0
            if i < len(roi_toc)-1:
                begin = p[1][-1]-1
                end = roi_toc[i+1][1][-1]-2
                cur_idx = p[0]
                next_idx = roi_toc[i+1][0]
            else:
                begin = p[1][-1]-1
                end = doc.page_count-1
                cur_idx = p[0]
                next_idx = len(toc)
            tmp_doc: fitz.Document = fitz.open()
            tmp_doc.insert_pdf(doc, from_page=begin, to_page=end)
            title = p[1][1].replace("/", "-").replace("\\", "-").replace(":", "-").replace("?","-").replace("*", "-").replace("\"", "-").replace("<", "-").replace(">", "-").replace("|", "-")

            tmp_toc = list(map(lambda x: [x[0], x[1], x[2]-begin],toc[cur_idx:next_idx]))
            tmp_doc.set_toc(tmp_toc)
            tmp_doc.save(str(output_dir / f"{title}.pdf"))
    except:
        logger.debug(p)
        raise ValueError(traceback.format_exc())

def reorder_pdf(doc_path: str, page_range: str = "all", output_path: str = None):
    try:
        doc: fitz.Document = fitz.open(doc_path)
        p = Path(doc_path)
        roi_indices = parse_range(page_range, doc.page_count, is_unique=False)
        logger.debug(roi_indices)
        if output_path is None:
            output_path = str(p.parent / f"{p.stem}-重排.pdf")
        tmp_doc: fitz.Document = fitz.open()
        for i in roi_indices:
            tmp_doc.insert_pdf(doc, from_page=i, to_page=i)
        tmp_doc.save(output_path, garbage=3, deflate=True)
    except:
        raise ValueError(traceback.format_exc())

def insert_blank_pdf(doc_path: str, pos: int, count: int, orientation: str, paper_size: str, output_path: str = None):
    try:
        doc: fitz.Document = fitz.open(doc_path)
        p = Path(doc_path)
        if output_path is None:
            output_path = str(p.parent / f"{p.stem}-插入空白页.pdf")
        tmp_doc: fitz.Document = fitz.open()
        fmt = fitz.paper_rect(f"{paper_size}-l") if orientation == "landscape" else fitz.paper_rect(paper_size)
        if pos - 2 >= 0:
            tmp_doc.insert_pdf(doc, from_page=0, to_page=pos-2)
        for i in range(count):
            tmp_doc.new_page(-1, width=fmt.width, height=fmt.height)
        tmp_doc.insert_pdf(doc, from_page=pos-1, to_page=-1)
        tmp_doc.save(output_path, garbage=3, deflate=True)
    except:
        raise ValueError(traceback.format_exc())

def insert_pdf(doc_path1: str, doc_path2: str, insert_pos: int, page_range: str = "all", output_path: str = None):
    try:
        doc1: fitz.Document = fitz.open(doc_path1)
        doc2: fitz.Document = fitz.open(doc_path2)
        page_range = page_range.strip()
        assert 1 <= insert_pos <= doc1.page_count, "插入位置超出范围!"
        n1, n2 = doc1.page_count, doc2.page_count
        if output_path is None:
            p = Path(doc_path1)
            output_path = str(p.parent / f"{p.stem}-插入.pdf")
        tmp_doc: fitz.Document = fitz.open()
        if insert_pos - 2 >= 0:
            tmp_doc.insert_pdf(doc1, from_page=0, to_page=insert_pos-2)
        doc2_indices = parse_range(page_range, n2)
        for i in doc2_indices:
            tmp_doc.insert_pdf(doc2, from_page=i, to_page=i)
        tmp_doc.insert_pdf(doc1, from_page=insert_pos-1, to_page=n1-1)
        tmp_doc.save(output_path, garbage=3, deflate=True)
    except:
        raise ValueError(traceback.format_exc())

def replace_pdf(doc_path1: str, doc_path2: str, src_range: str = "all", dst_range: str = "all", output_path: str = None):
    try:
        doc1: fitz.Document = fitz.open(doc_path1)
        doc2: fitz.Document = fitz.open(doc_path2)
        src_range = src_range.strip()
        dst_range = dst_range.strip()
        n1, n2 = doc1.page_count, doc2.page_count
        if re.match("^!?(\d+|N)(\-(\d+|N))?$", src_range) is None:
            raise ValueError("源页码格式错误!")
        if output_path is None:
            p = Path(doc_path1)
            output_path = str(p.parent / f"{p.stem}-替换.pdf")
        tmp_doc: fitz.Document = fitz.open()
        dst_indices = parse_range(dst_range, n2)
        parts = src_range.split("-")
        if len(parts) == 2:
            a, b = parts
            a = int(a) if a != "N" else n1
            b = int(b) if b != "N" else n1
            tmp_doc.insert_pdf(doc1, from_page=0, to_page=a-2)
            for i in dst_indices:
                tmp_doc.insert_pdf(doc2, from_page=i, to_page=i)
            tmp_doc.insert_pdf(doc1, from_page=b, to_page=n1-1)
            tmp_doc.save(output_path, garbage=3, deflate=True)
        elif len(parts) == 1:
            a = int(parts[0]) if parts[0] != "N" else n1
            tmp_doc.insert_pdf(doc1, from_page=0, to_page=a-2)
            for i in dst_indices:
                tmp_doc.insert_pdf(doc2, from_page=i, to_page=i)
            if a < n1:
                tmp_doc.insert_pdf(doc1, from_page=a, to_page=n1-1)
            tmp_doc.save(output_path, garbage=3, deflate=True)
        else:
            raise ValueError("页码格式错误!")
    except:
        raise ValueError(traceback.format_exc())

def merge_pdf(doc_path_list: List[str], sort_method: str = "default", sort_direction: str = "asc", output_path: str = None):
    try:
        new_path_list = []
        for doc_path in doc_path_list:
            if "*" in doc_path:
                path_list = glob.glob(doc_path)
                if path_list:
                    new_path_list.extend(path_list)
            else:
                new_path_list.append(doc_path)
        if sort_method == "default":
            if sort_direction == "asc":
                pass
            else:
                new_path_list = new_path_list[::-1]
        elif sort_method == "name":
            if sort_direction == "asc":
                new_path_list.sort()
            else:
                new_path_list.sort(reverse=True)
        # create time
        elif sort_method == "ctime":
            if sort_direction == "asc":
                new_path_list.sort(key=lambda x: Path(x).stat().st_ctime)
            else:
                new_path_list.sort(key=lambda x: Path(x).stat().st_ctime, reverse=True)
        # modify time
        elif sort_method == "mtime":
            if sort_direction == "asc":
                new_path_list.sort(key=lambda x: Path(x).stat().st_mtime)
            else:
                new_path_list.sort(key=lambda x: Path(x).stat().st_mtime, reverse=True)
        logger.debug(new_path_list)
        doc: fitz.Document = fitz.open()
        for doc_path in new_path_list:
            doc_temp = fitz.open(doc_path)
            doc.insert_pdf(doc_temp)
        if output_path is None:
            p = Path(doc_path_list[0])
            output_path = str(p.parent / f"合并.pdf")
        doc.save(output_path)
    except:
        raise ValueError(traceback.format_exc())

def rotate_pdf(doc_path: str, angle: int, page_range: str = "all", output_path: str = None):
    try:
        doc: fitz.Document = fitz.open(doc_path)
        roi_indices = parse_range(page_range, doc.page_count)
        for page_index in roi_indices:
            page = doc[page_index]
            page.set_rotation(angle)
            
        if output_path is None:
            p = Path(doc_path)
            output_path = str(p.parent / f"{p.stem}-旋转.pdf")
        doc.save(output_path)
    except:
        raise ValueError(traceback.format_exc())

def crop_pdf(doc_path: str, bbox: Tuple[int, int, int, int], page_range: str = "all", output_path: str = None):
    try:
        doc: fitz.Document = fitz.open(doc_path)
        roi_indices = parse_range(page_range, doc.page_count)
        for page_index in roi_indices:
            page = doc[page_index]
            page.set_cropbox(fitz.Rect(*bbox))
            
        if output_path is None:
            p = Path(doc_path)
            output_path = str(p.parent / f"{p.stem}-裁剪.pdf")
        doc.save(output_path)
    except:
        raise ValueError(traceback.format_exc())

def cut_pdf_by_grid(doc_path: str, n_row: int, n_col: int, page_range: str = "all", output_path: str = None):
    try:
        doc: fitz.Document = fitz.open(doc_path)
        roi_indices = parse_range(page_range, doc.page_count)
        tmp_doc: fitz.Document = fitz.open()
        for page_index in roi_indices:
            page = doc[page_index]
            page_width, page_height = page.rect.width, page.rect.height
            # CropBox displacement if not starting at (0, 0)
            # d = fitz.Rect(page.cropbox_position, page.cropbox_position)
            width, height = page_width/n_col, page_height/n_row
            for i in range(n_row):
                for j in range(n_col):
                    bbox = fitz.Rect(j*width, i*height, (j+1)*width, (i+1)*height)
                    # bbox += d
                    tmp_page = tmp_doc.new_page(-1, width=bbox.width, height=bbox.height)
                    tmp_page.show_pdf_page(tmp_page.rect, doc, page_index, clip=bbox)
        if output_path is None:
            p = Path(doc_path)
            output_path = str(p.parent / f"{p.stem}-网格分割.pdf")
        tmp_doc.save(output_path, garbage=3, deflate=True)
    except:
        raise ValueError(traceback.format_exc())

def cut_pdf_by_breakpoints(doc_path: str, h_breakpoints: List[float], v_breakpoints: List[float], page_range: str = "all", output_path: str = None):
    try:
        doc: fitz.Document = fitz.open(doc_path)
        roi_indices = parse_range(page_range, doc.page_count)
        tmp_doc: fitz.Document = fitz.open()
        h_breakpoints = [v for v in h_breakpoints if 0 <= v <= 1]
        h_breakpoints = [0] + h_breakpoints + [1]
        h_breakpoints.sort()
        v_breakpoints = [v for v in v_breakpoints if 0 <= v <= 1]
        v_breakpoints = [0] + v_breakpoints + [1]
        v_breakpoints.sort()
        for page_index in roi_indices:
            page = doc[page_index]
            page_width, page_height = page.rect.width, page.rect.height
            # CropBox displacement if not starting at (0, 0)
            d = fitz.Rect(page.cropbox_position, page.cropbox_position)
            for i in range(len(h_breakpoints)-1):
                for j in range(len(v_breakpoints)-1):
                    bbox = fitz.Rect(v_breakpoints[j]*page_width, h_breakpoints[i]*page_height, v_breakpoints[j+1]*page_width, h_breakpoints[i+1]*page_height,)
                    bbox += d
                    tmp_page = tmp_doc.new_page(-1, width=bbox.width, height=bbox.height)
                    tmp_page.show_pdf_page(tmp_page.rect, doc, page_index, clip=bbox)
        if output_path is None:
            p = Path(doc_path)
            output_path = str(p.parent / f"{p.stem}-自定义分割.pdf")
        tmp_doc.save(output_path, garbage=3, deflate=True)
    except:
        raise ValueError(traceback.format_exc())

def combine_pdf_by_grid(doc_path, n_row: int, n_col: int, paper_size: str = "a4", orientation: str = "portrait", page_range: str = "all", output_path: str = None):
    try:
        doc: fitz.Document = fitz.open(doc_path)
        if orientation == "landscape":
            paper_size = f"{paper_size}-l"
        width, height = fitz.paper_size(paper_size)
        batch_size = n_row * n_col
        unit_w, unit_h = width / n_col, height / n_row
        r_tab = []
        for i in range(n_row):
            for j in range(n_col):
                rect = fitz.Rect(j*unit_w, i*unit_h, (j+1)*unit_w, (i+1)*unit_h)
                r_tab.append(rect)
        tmp_doc: fitz.Document = fitz.open()
        roi_indices = parse_range(page_range, doc.page_count)
        for page_index in roi_indices:
            if page_index % batch_size == 0:
                page = tmp_doc.new_page(-1, width=width, height=height)
            page.show_pdf_page(r_tab[page_index % batch_size], doc, page_index)
        tmp_doc.save(output_path, garbage=3, deflate=True)
    except:
        raise ValueError(traceback.format_exc())

def extract_pdf_images(doc_path: str, page_range: str = "all", output_path: str = None):
    try:
        doc: fitz.Document = fitz.open(doc_path)
        roi_indicies = parse_range(page_range, doc.page_count)
        if output_path is None:
            p = Path(doc_path)
            output_path = str(p.parent / f"{p.stem}-图片")
            Path(output_path).mkdir(parents=True, exist_ok=True)
        else:
            Path(output_path).mkdir(parents=True, exist_ok=True)
        for page_index in roi_indicies:
            page = doc[page_index]
            image_list = page.get_images()
            for i, img in enumerate(image_list):
                xref = img[0] # get the XREF of the image
                pix = fitz.Pixmap(doc, xref) # create a Pixmap
                if pix.n - pix.alpha > 3: # CMYK: convert to RGB first
                    pix = fitz.Pixmap(fitz.csRGB, pix)
                savepath = str(Path(output_path) / f"{page_index+1}-{i+1}.png")
                pix.save(savepath) # save the image as PNG
                pix = None
    except:
        raise ValueError(traceback.format_exc())

def extract_pdf_text(doc_path: str, page_range: str = "all", output_path: str = None):
    try:
        doc: fitz.Document = fitz.open(doc_path)
        roi_indicies = parse_range(page_range, doc.page_count)
        if output_path is None:
            p = Path(doc_path)
            output_path = str(p.parent / f"{p.stem}-文本")
            Path(output_path).mkdir(parents=True, exist_ok=True)
        else:
            Path(output_path).mkdir(parents=True, exist_ok=True)
        for page_index in roi_indicies:
            page = doc[page_index]
            text = page.get_text()
            savepath = str(Path(output_path) / f"{page_index+1}.txt")
            with open(savepath, "w", encoding="utf-8") as f:
                f.write(text)
    except:
        raise ValueError(traceback.format_exc())

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
        
        return {'level': 1, "text": title}

def add_toc_from_file(toc_path: str, doc_path: str, offset: int, output_path: str = None):
    """从目录文件中导入书签到pdf文件(若文件中存在行没指定页码则按1算)

    Args:
        toc_path (str): 目录文件路径
        doc_path (str): pdf文件路径
        offset (int): 偏移量, 计算方式: “pdf文件实际页码” - “目录文件标注页码”
    """
    doc: fitz.Document = fitz.open(doc_path)
    p = Path(doc_path)
    toc_path = Path(toc_path)
    toc = []
    if toc_path.suffix == ".txt":
        with open(toc_path, "r", encoding="utf-8") as f:
            for line in f:
                pno = 1
                title = line
                m = re.search("(\d+)(?=\s*$)", line) # 把最右侧的数字当作页码，如果解析的数字超过pdf总页数，就从左边依次删直到小于pdf总页数为止
                if m is not None:
                    pno = int(m.group(1))
                    while pno > doc.page_count:
                        pno = int(str(pno)[1:])
                    title = line[:m.span()[0]]
                pno = pno + offset
                if not title.strip(): # 标题为空跳过
                    continue
                res = title_preprocess(title)
                level, title = res['level'], res['text']
                toc.append([level, title, pno])
    elif toc_path.suffix == ".json":
        with open(toc_path, "r", encoding="utf-8") as f:
            toc = json.load(f)
    else:
        raise ValueError("不支持的toc文件格式!")
    # 校正层级
    levels = [v[0] for v in toc]
    diff = [levels[i+1]-levels[i] for i in range(len(levels)-1)]
    indices = [i for i in range(len(diff)) if diff[i] > 1]
    for idx in indices:
        toc[idx][0] = toc[idx+1][0]
    doc.set_toc(toc)
    if output_path is None:
        output_path = str(p.parent / f"{p.stem}-toc.pdf")
    doc.save(output_path)

def add_toc_by_gap(doc_path: str, gap: int = 1, format: str = "第%p页", output_path: str = None):
    doc: fitz.Document = fitz.open(doc_path)
    p = Path(doc_path)
    toc = []
    for i in range(0, doc.page_count, gap):
        toc.append([1, format.replace("%p", str(i+1)), i+1])
    toc.append([1, format.replace("%p", str(doc.page_count)), doc.page_count])
    doc.set_toc(toc)
    if output_path is None:
        output_path = str(p.parent / f"{p.stem}-[页码书签版].pdf")
    doc.save(output_path)

def extract_toc(doc_path: str, format: str = "txt", output_path: str = None):
    doc: fitz.Document = fitz.open(doc_path)
    p = Path(doc_path)
    toc = doc.get_toc(simple=False)
    if format == "txt":
        if output_path is None:
            output_path = str(p.parent / f"{p.stem}-toc.txt")
        with open(output_path, "w", encoding="utf-8") as f:
            for line in toc:
                indent = (line[0]-1)*"\t"
                f.writelines(f"{indent}{line[1]} {line[2]}\n")
    elif format == "json":
        if output_path is None:
            output_path = str(p.parent / f"{p.stem}-toc.json")
        for i in range(len(toc)):
            try:
                toc[i][-1] = toc[i][-1]['to'].y
            except:
                toc[i][-1] = 0
        with open(output_path, "w", encoding="utf-8") as f:
            json.dump(toc, f)

def transform_toc_file(toc_path: str, is_add_indent: bool = True, is_remove_trailing_dots: bool = True, add_offset: int = 0, output_path: str = None):
    if output_path is None:
        p = Path(toc_path)
        output_path = str(p.parent / f"{p.stem}-toc-clean.txt")
    with open(toc_path, "r", encoding="utf-8") as f, open(output_path, "w", encoding="utf-8") as f2:
        for line in f:
            new_line = line
            if is_remove_trailing_dots:
                new_line = re.sub("(\.\s*)+(?=\d*\s*$)", " ", new_line)
                new_line = new_line.rstrip() + "\n"
            if is_add_indent:
                res = title_preprocess(new_line)
                new_line = (res['level']-1)*'\t' + res['text'] + "\n"
            if add_offset:
                m = re.search("(\d+)(?=\s*$)", new_line)
                if m is not None:
                    pno = int(m.group(1))
                    pno = pno + add_offset
                    new_line = new_line[:m.span()[0]-1] + f" {pno}\n"
            f2.write(new_line)

def encrypt_pdf(doc_path: str, user_password: str, owner_password: str = None, perm: List[str] = [], output_path: str = None):
    doc: fitz.Document = fitz.open(doc_path)
    p = Path(doc_path)
    full_perm_dict = {
        "打开": fitz.PDF_PERM_ACCESSIBILITY,
        "复制": fitz.PDF_PERM_COPY,
        "打印": fitz.PDF_PERM_PRINT | fitz.PDF_PERM_PRINT_HQ,
        "注释": fitz.PDF_PERM_ANNOTATE,
        "表单": fitz.PDF_PERM_FORM,
        "插入/删除页面": fitz.PDF_PERM_ASSEMBLE,
    }
    for v in perm:
        del full_perm_dict[v]
    perm_value = sum(full_perm_dict.values())
    encrypt_meth = fitz.PDF_ENCRYPT_AES_256 # strongest algorithm
    if output_path is None:
        output_path = str(p.parent / f"{p.stem}-加密.pdf")
    doc.save(
        output_path,
        encryption=encrypt_meth, # set the encryption method
        owner_pw=owner_password, # set the owner password
        user_pw=user_password, # set the user password
        permissions=perm_value, # set permissions
    )

def decrypt_pdf(doc_path: str, password: str, output_path: str = None):
    doc: fitz.Document = fitz.open(doc_path)
    p = Path(doc_path)
    if doc.isEncrypted:
        doc.authenticate(password)
        n = doc.page_count
        doc.select(range(n))
    if output_path is None:
        output_path = str(p.parent / f"{p.stem}-解密.pdf")
    doc.save(output_path)

def compress_pdf(doc_path: str, output_path: str = None):
    doc: fitz.Document = fitz.open(doc_path)
    p = Path(doc_path)
    if output_path is None:
        output_path = str(p.parent / f"{p.stem}-压缩.pdf")
    doc.save(output_path, garbage=4, deflate=True, clean=True)

def resize_pdf_by_dim(doc_path: str, width: float, height: float, page_range: str = "all", output_path: str = None):
    try:
        doc: fitz.Document = fitz.open(doc_path)
        p = Path(doc_path)
        if output_path is None:
            output_path = str(p.parent / f"{p.stem}-缩放.pdf")
        new_doc: fitz.Document = fitz.open()
        roi_indices = parse_range(page_range, doc.page_count)
        for i in range(doc.page_count):
            if i not in roi_indices:
                new_doc.insert_pdf(doc, from_page=i, to_page=i)
                continue
            page = doc[i]
            new_page: fitz.Page = new_doc.new_page(width=width, height=height)
            new_page.show_pdf_page(new_page.rect, doc, page.number, rotate=page.rotation)
        new_doc.save(output_path)
    except:
        raise ValueError(traceback.format_exc())

def resize_pdf_by_scale(doc_path: str, scale: float, page_range: str = "all", output_path: str = None):
    try:
        doc: fitz.Document = fitz.open(doc_path)
        p = Path(doc_path)
        if output_path is None:
            output_path = str(p.parent / f"{p.stem}-缩放.pdf")
        new_doc: fitz.Document = fitz.open()
        roi_indices = parse_range(page_range, doc.page_count)
        for i in range(doc.page_count):
            if i not in roi_indices:
                new_doc.insert_pdf(doc, from_page=i, to_page=i)
                continue
            page = doc[i]
            new_page: fitz.Page = new_doc.new_page(width=page.rect.width*scale, height=page.rect.height*scale)
            new_page.show_pdf_page(new_page.rect, doc, page.number, rotate=page.rotation)
        new_doc.save(output_path)
    except:
        raise ValueError(traceback.format_exc())

def resize_pdf_by_paper_size(doc_path: str, paper_size: str, page_range: str = "all", output_path: str = None):
    try:
        doc: fitz.Document = fitz.open(doc_path)
        p = Path(doc_path)
        if output_path is None:
            output_path = str(p.parent / f"{p.stem}-缩放.pdf")
        new_doc: fitz.Document = fitz.open()
        roi_indices = parse_range(page_range, doc.page_count)
        for i in range(doc.page_count):
            if i not in roi_indices:
                new_doc.insert_pdf(doc, from_page=i, to_page=i)
                continue
            page = doc[i]
            if page.rect.width > page.rect.height:
                fmt = fitz.paper_rect(f"{paper_size}-l")
            else:
                fmt = fitz.paper_rect(f"{paper_size}")
            new_page: fitz.Page = new_doc.new_page(width=fmt.width, height=fmt.height)
            new_page.show_pdf_page(new_page.rect, doc, page.number, rotate=page.rotation)
        new_doc.save(output_path)
    except:
        raise ValueError(traceback.format_exc())

def main():
    parser = argparse.ArgumentParser()
    sub_parsers = parser.add_subparsers()
    # 合并子命令
    merge_parser = sub_parsers.add_parser("merge", help="合并", description="合并pdf文件")
    merge_parser.set_defaults(which='merge')
    merge_parser.add_argument("input_path_list", type=str, nargs="+", help="pdf文件路径")
    merge_parser.add_argument("-o", "--output", type=str, help="输出文件路径")
    merge_parser.add_argument("--sort_method", type=str, choices=['default', 'name', 'ctime', 'mtime'], default="default", help="排序方式")
    merge_parser.add_argument("--sort_direction", type=str, choices=['asc', 'desc'], default="asc", help="排序方向")

    # 拆分子命令
    split_parser = sub_parsers.add_parser("split", help="拆分", description="拆分pdf文件")
    split_parser.set_defaults(which='split')
    split_parser.add_argument("input_path", type=str, help="pdf文件路径")
    split_parser.add_argument("--mode", type=str, choices=['chunk', 'page', 'toc'], default="chunk", help="拆分模式")
    split_parser.add_argument("--page_range", type=str, default="all", help="页码范围")
    split_parser.add_argument("--chunk_size", type=int, default=10, help="拆分块大小")
    split_parser.add_argument("-o", "--output", type=str, help="输出文件路径")
    split_parser.add_argument("--toc-level", type=int, default=1, help="目录层级")

    #  删除子命令
    delete_parser = sub_parsers.add_parser("delete", help="删除", description="删除pdf文件")
    delete_parser.set_defaults(which='delete')
    delete_parser.add_argument("input_path", type=str, help="pdf文件路径")
    delete_parser.add_argument("--page_range", type=str, default="all", help="页码范围")
    delete_parser.add_argument("-o", "--output", type=str, help="输出文件路径")

    # 插入子命令
    insert_parser = sub_parsers.add_parser("insert", help="插入", description="插入pdf文件")
    insert_parser.set_defaults(which='insert')
    insert_parser.add_argument("--method", type=str, choices=['blank', 'pdf'], default="pdf", help="插入方式")
    insert_parser.add_argument("input_path1", type=str, help="被插入的pdf文件路径")
    insert_parser.add_argument("input_path2", type=str, help="插入pdf文件路径")
    insert_parser.add_argument("--insert_pos", type=int, default=0, help="插入位置")
    insert_parser.add_argument("--page_range", type=str, default="all", help="插入pdf的页码范围")
    insert_parser.add_argument("--orientation", type=str, choices=['portrait', 'landscape'], default="portrait", help="纸张方向")
    insert_parser.add_argument("--paper_size", type=str, default="A4", help="纸张大小")
    insert_parser.add_argument("--count", type=int, default=1, help="插入数量")
    insert_parser.add_argument("-o", "--output", type=str, help="输出文件路径")

    # 替换子命令
    replace_parser = sub_parsers.add_parser("replace", help="替换", description="替换pdf文件")
    replace_parser.set_defaults(which='replace')
    replace_parser.add_argument("input_path1", type=str, help="被替换的pdf文件路径")
    replace_parser.add_argument("input_path2", type=str, help="替换pdf文件路径")
    replace_parser.add_argument("--src_page_range", type=str, default="all", help="页码范围")
    replace_parser.add_argument("--dst_page_range", type=str, default="all", help="页码范围")
    replace_parser.add_argument("-o", "--output", type=str, help="输出文件路径")

    # 旋转子命令
    rotate_parser = sub_parsers.add_parser("rotate", help="旋转", description="旋转pdf文件")
    rotate_parser.set_defaults(which='rotate')
    rotate_parser.add_argument("input_path", type=str, help="pdf文件路径")
    rotate_parser.add_argument("--page_range", type=str, default="all", help="页码范围")
    rotate_parser.add_argument("--angle", type=int, default=90, help="旋转角度")
    rotate_parser.add_argument("-o", "--output", type=str, help="输出文件路径")

    # 加密子命令
    encrypt_parser = sub_parsers.add_parser("encrypt", help="加密", description="加密pdf文件")
    encrypt_parser.add_argument("input_path", type=str, help="pdf文件路径")
    encrypt_parser.add_argument("--user_password", type=str, help="用户密码")
    encrypt_parser.add_argument("--owner_password", type=str, help="所有者密码")
    encrypt_parser.add_argument("--perm", type=str, nargs="+", help="权限")
    encrypt_parser.add_argument("-o", "--output", type=str, help="输出文件路径")
    encrypt_parser.set_defaults(which='encrypt')
    
    # 重排子命令
    reorder_parser = sub_parsers.add_parser("reorder", help="重排", description="重排pdf文件")
    reorder_parser.set_defaults(which='reorder')
    reorder_parser.add_argument("input_path", type=str, help="pdf文件路径")
    reorder_parser.add_argument("--page_range", type=str, default="all", help="页码范围")
    reorder_parser.add_argument("-o", "--output", type=str, help="输出文件路径")

    # 解密子命令
    decrypt_parser = sub_parsers.add_parser("decrypt", help="解密", description="解密pdf文件")
    decrypt_parser.add_argument("input_path", type=str, help="pdf文件路径")
    decrypt_parser.add_argument("--password", type=str, help="密码")
    decrypt_parser.add_argument("-o", "--output", type=str, help="输出文件路径")
    decrypt_parser.set_defaults(which='decrypt')
    
    # 书签子命令
    bookmark_parser = sub_parsers.add_parser("bookmark", help="书签", description="添加、提取、转换书签")
    bookmark_sub_parsers = bookmark_parser.add_subparsers()
    bookmark_parser.set_defaults(which='bookmark')

    ## 添加书签
    bookmark_add_parser = bookmark_sub_parsers.add_parser("add", help="添加书签")
    ### 文件书签
    bookmark_add_parser.add_argument("input_path", type=str, help="pdf文件路径")
    bookmark_add_parser.add_argument("--method", type=str, choices=['file', 'gap'], default="file", help="添加方式")
    bookmark_add_parser.add_argument("--toc", type=str, help="目录文件路径")
    bookmark_add_parser.add_argument("--offset", type=int, default=0, help="偏移量, 计算方式: “pdf文件实际页码” - “目录文件标注页码”")
    bookmark_add_parser.add_argument("-o", "--output", type=str, help="输出文件路径")
    bookmark_add_parser.set_defaults(bookmark_which='add')
    
    ### 页码书签
    bookmark_add_parser.add_argument("--gap", type=int, default=1, help="页码间隔")
    bookmark_add_parser.add_argument("--format", type=str, default="第%p页", help="页码格式")
    
    ## 提取书签
    bookmark_extract_parser = bookmark_sub_parsers.add_parser("extract", help="提取书签")
    bookmark_extract_parser.add_argument("input_path", type=str, help="pdf文件路径")
    bookmark_extract_parser.add_argument("--format", type=str, default="txt", choices=['txt', 'json'], help="输出文件格式")
    bookmark_extract_parser.add_argument("-o", "--output", type=str, help="输出文件路径")
    bookmark_extract_parser.set_defaults(bookmark_which='extract')
    
    ## 书签转换
    bookmark_transform_parser = bookmark_sub_parsers.add_parser("transform", help="转换书签")
    bookmark_transform_parser.add_argument("--toc", type=str, help="目录文件路径")
    bookmark_transform_parser.add_argument("--add_indent", action="store_true", help="是否添加缩进")
    bookmark_transform_parser.add_argument("--remove_trailing_dots", action="store_true", help="是否删除标题末尾的点号")
    bookmark_transform_parser.add_argument("--add_offset", type=int, default=0, help="页码偏移量")
    bookmark_transform_parser.add_argument("-o", "--output", type=str, help="输出文件路径")
    bookmark_transform_parser.set_defaults(bookmark_which='transform')

    # 水印子命令
    watermark_parser = sub_parsers.add_parser("watermark", help="水印", description="添加文本水印")
    watermark_parser.add_argument("input_path", type=str, help="pdf文件路径")
    watermark_parser.add_argument("--mark-text", type=str, required=True, dest="mark_text", help="水印文本")
    watermark_parser.add_argument("--font-family", type=str, dest="font_family", help="水印字体路径")
    watermark_parser.add_argument("--font-size", type=int, default=50, dest="font_size", help="水印字体大小")
    watermark_parser.add_argument("--color", type=str, default="#808080", dest="color", help="水印文本颜色")
    watermark_parser.add_argument("--angle", type=int, default=30, dest="angle", help="水印旋转角度")
    watermark_parser.add_argument("--space", type=int, default=75, dest="space", help="水印文本间距")
    watermark_parser.add_argument("--opacity", type=float, default=0.15, dest="opacity", help="水印不透明度")
    watermark_parser.add_argument("--font-height-crop", type=str, default="1.2", dest="font_height_crop")
    watermark_parser.add_argument("--quality", type=int, default=80, dest="quality", help="水印图片保存质量")
    watermark_parser.add_argument("-o", "--output", type=str, help="输出文件路径")
    watermark_parser.set_defaults(which='watermark')
    
    # 压缩子命令
    compress_parser = sub_parsers.add_parser("compress", help="压缩", description="压缩pdf文件")
    compress_parser.add_argument("input_path", type=str, help="pdf文件路径")
    compress_parser.add_argument("-o", "--output", type=str, help="输出文件路径")
    compress_parser.set_defaults(which='compress')

    # 缩放子命令
    resize_parser = sub_parsers.add_parser("resize", help="缩放", description="缩放pdf文件")
    resize_parser.set_defaults(which='resize')
    resize_parser.add_argument("input_path", type=str, help="pdf文件路径")
    resize_parser.add_argument("--method", type=str, choices=['dim', 'scale', 'paper_size'], default="dim", help="缩放方式")
    resize_parser.add_argument("--width", type=float, help="宽度")
    resize_parser.add_argument("--height", type=float, help="高度")
    resize_parser.add_argument("--scale", type=float, help="缩放比例")
    resize_parser.add_argument("--paper_size", type=str, help="纸张大小")
    resize_parser.add_argument("--page_range", type=str, default="all", help="页码范围")
    resize_parser.add_argument("-o", "--output", type=str, help="输出文件路径")

    # 提取子命令
    extract_parser = sub_parsers.add_parser("extract", help="提取", description="提取pdf文件")
    extract_parser.set_defaults(which='extract')
    extract_parser.add_argument("input_path", type=str, help="pdf文件路径")
    extract_parser.add_argument("--page_range", type=str, default="all", help="页码范围")
    extract_parser.add_argument("--type", type=str, choices=['text', 'image'], default="text", help="提取类型")
    extract_parser.add_argument("-o", "--output", type=str, help="输出文件路径")

    # 分割子命令
    cut_parser = sub_parsers.add_parser("cut", help="分割", description="分割pdf文件")
    cut_parser.set_defaults(which='cut')
    cut_parser.add_argument("input_path", type=str, help="pdf文件路径")
    cut_parser.add_argument("--method", type=str, choices=['grid', 'breakpoints'], default="grid", help="分割模式")
    cut_parser.add_argument("--page_range", type=str, default="all", help="页码范围")
    cut_parser.add_argument("--h_breakpoints", type=float, nargs="+", help="水平分割点")
    cut_parser.add_argument("--v_breakpoints", type=float, nargs="+", help="垂直分割点")
    cut_parser.add_argument("--nrow", type=int, default=1, help="行数")
    cut_parser.add_argument("--ncol", type=int, default=1, help="列数")
    cut_parser.add_argument("-o", "--output", type=str, help="输出文件路径")

    # 组合子命令
    combine_parser = sub_parsers.add_parser("combine", help="组合", description="组合pdf文件")
    combine_parser.set_defaults(which='combine')
    combine_parser.add_argument("input_path", type=str, help="pdf文件路径")
    combine_parser.add_argument("--page_range", type=str, default="all", help="页码范围")
    combine_parser.add_argument("--method", type=str, choices=['grid', 'breakpoints'], default="grid", help="分割模式")

    args = parser.parse_args()
    logger.debug(args)
    if args.which == "merge":
        merge_pdf(args.input_path_list, args.sort_method, args.sort_direction, args.output)
    elif args.which == "split":
        if args.mode == "chunk":
            split_pdf_by_chunk(args.input_path, args.chunk_size, args.output)
        elif args.mode == "page":
            split_pdf_by_page(args.input_path, args.page_range, args.output)
        elif args.mode == "toc":
            split_pdf_by_toc(args.input_path, args.toc_level, args.output)
    elif args.which == "delete":
        slice_pdf(args.input_path, args.page_range, args.output, is_reverse=True)
    elif args.which == 'insert':
        if args.method == "blank":
            insert_blank_pdf(args.input_path1, args.insert_pos, args.count, args.orientation, args.paper_size, args.output)
        else:
            insert_pdf(args.input_path1, args.input_path2, args.insert_pos, args.page_range, args.output)
    elif args.which == "replace":
        replace_pdf(args.input_path1, args.input_path2, args.src_page_range, args.dst_page_range, args.output)
    elif args.which == "reorder":
        reorder_pdf(args.input_path, args.page_range, args.output)
    elif args.which == "rotate":
        rotate_pdf(args.input_path, args.angle, args.page_range, args.output)
    elif args.which == "encrypt":
        encrypt_pdf(args.input_path, args.user_password, args.owner_password, args.perm, args.output)
    elif args.which == "decrypt":
        decrypt_pdf(args.input_path, args.password, args.output)
    elif args.which == "compress":
        compress_pdf(args.input_path, args.output)
    elif args.which == "resize":
        if args.method == "dim":
            resize_pdf_by_dim(args.input_path, args.width, args.height, args.page_range, args.output)
        elif args.method == "scale":
            resize_pdf_by_scale(args.input_path, args.scale, args.page_range, args.output)
        elif args.method == "paper_size":
            resize_pdf_by_paper_size(args.input_path, args.paper_size, args.page_range, args.output)
    elif args.which == "bookmark":
        if args.bookmark_which == "add":
            if args.method == "file":
                add_toc_from_file(args.toc, args.input_path, args.offset, args.output)
            elif args.method == "gap":
                add_toc_by_gap(args.input_path, args.gap, args.format, args.output)
        elif args.bookmark_which == "extract":
            extract_toc(args.input_path, args.format, args.output)
        elif args.bookmark_which == "transform":
            transform_toc_file(args.toc, args.add_indent, args.remove_trailing_dots, args.add_offset, args.output)
    elif args.which == "extract":
        if args.type == "text":
            extract_pdf_text(args.input_path, args.page_range, args.output)
        elif args.type == "image":
            extract_pdf_images(args.input_path, args.page_range, args.output)
        else:
            raise ValueError("不支持的提取类型!")
    elif args.which == "cut":
        if args.method == "grid":
            cut_pdf_by_grid(args.input_path, args.nrow, args.ncol, args.page_range, args.output)
        elif args.method == "breakpoints":
            cut_pdf_by_breakpoints(args.input_path, args.h_breakpoints, args.v_breakpoints, args.page_range, args.output)
    elif args.which == "watermark":
        mark_args = {
            "font_family": args.font_family,
            "size": args.font_size,
            "space": args.space,
            "angle": args.angle,
            "color": args.color,
            "opacity": args.opacity,
            "font_height_crop": "1.2",
        }
        if args.input_path.endswith(".pdf"):
            # add_mark_to_pdf(doc_path=args.input_path, output_path=args.output, mark_text=args.mark_text, quality=args.quality, **mark_args)
            pass
        else:
            raise ValueError("不支持的文件格式!")

def create_wartmark(
        content:str,
        path:str,
        width: Union[int, float],
        height: Union[int, float],
        font: str,
        fontsize: int,
        angle: Union[int, float] = 45,
        text_stroke_color_rgb: Tuple[int, int, int] = (0, 0, 0),
        text_fill_color_rgb: Tuple[int, int, int] = (0, 0, 0),
        text_fill_alpha: Union[int, float] = 1
    ) -> None:
    c = canvas.Canvas(path,pagesize=(width*units.mm,height*units.mm))
    c.translate(0.1*width*units.mm,0.1*height*units.mm)
    c.rotate(angle)
    c.setFont(font,fontsize)
    c.setStrokeColorRGB(*text_stroke_color_rgb)
    c.setFillColorRGB(*text_fill_color_rgb)
    c.setFillAlpha(text_fill_alpha)
    c.drawString(0,0,content)
    c.setCropBox([0, 0, 100*units.mm, 30*units.mm])
    c.save()

if __name__ == "__main__":
    main()
    # print(parse_range("1-4", 10, is_reverse=True))
    # extract_pdf_images(r"C:\Users\kevin\Downloads\pdfcpu_0.4.1_Windows_x86_64\九章算法-decrypt.pdf")