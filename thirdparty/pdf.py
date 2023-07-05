import argparse
import glob
import json
import os
import re
import math
import subprocess
import traceback
from pathlib import Path
from typing import List, Tuple, Union
import random
import fitz
from loguru import logger
from PIL import Image, ImageChops, ImageDraw, ImageEnhance, ImageFont, ImageOps
from pypdf import PdfReader, PdfWriter
from reportlab.lib import units
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.pdfgen import canvas
import colorsys

# 工具类函数
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

def convert_length(length, from_unit, to_unit):
    """
    将长度从一个单位转换为另一个单位
    :param length: 长度值
    :param from_unit: 原单位，可选值："pt"、"cm"、"mm"、"in"、"px"
    :param to_unit: 目标单位，可选值："pt"、"cm"、"mm"、"in"、"px"
    :param dpi: 屏幕或打印机的分辨率，默认为每英寸72个点（即标准屏幕分辨率）
    :return: 转换后的长度值
    """

    units = {"pt": 1, "cm": 2.54/72, "mm": 25.4/72, "in": 1/72}
    if from_unit not in units or to_unit not in units:
        raise ValueError("Invalid unit")

    pt_length = length / units[from_unit]
    return pt_length * units[to_unit]

def hex_to_rgb(hex_color):
    # 去掉 # 号并解析为十六进制数值
    hex_value = hex_color.lstrip("#")
    # 解析 R、G、B 三个十六进制数值
    r, g, b = tuple(int(hex_value[i:i+2], 16) for i in (0, 2, 4))
    # 将 R、G、B 转换为 RGB 颜色值
    rgb_color = colorsys.rgb_to_hsv(r/255, g/255, b/255)
    return tuple(round(c * 255) for c in colorsys.hsv_to_rgb(*rgb_color))

# 功能类函数

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
        if paper_size == "same":
            fmt = doc[0].rect
        else:
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

def crop_pdf_by_bbox(doc_path: str, bbox: Tuple[int, int, int, int], unit: str = "pt", keep_page_size: bool = True, page_range: str = "all", output_path: str = None):
    try:
        doc: fitz.Document = fitz.open(doc_path)
        roi_indices = parse_range(page_range, doc.page_count)
        tmp_doc: fitz.Document = fitz.open()
        if unit != "pt":
            bbox = tuple(map(lambda x: convert_length(x, unit, "pt"), bbox))
            logger.debug(bbox)
        for page_index in roi_indices:
            page = doc[page_index]
            page_width, page_height = page.rect.width, page.rect.height
            if keep_page_size:
                new_page = tmp_doc.new_page(-1, width=page_width, height=page_height)
                new_page.show_pdf_page(new_page.rect, doc, page_index, clip=bbox)
            else:
                new_page = tmp_doc.new_page(-1, width=bbox[2]-bbox[0], height=bbox[3]-bbox[1])
                new_page.show_pdf_page(new_page.rect, doc, page_index, clip=bbox)
        if output_path is None:
            p = Path(doc_path)
            output_path = str(p.parent / f"{p.stem}-裁剪.pdf")
        tmp_doc.save(output_path, garbage=3, deflate=True)
    except:
        raise ValueError(traceback.format_exc())

def crop_pdf_by_page_margin(doc_path: str, margin: Tuple[int, int, int, int], unit: str = "pt", keep_page_size: bool = True, page_range: str = "all", output_path: str = None):
    try:
        doc: fitz.Document = fitz.open(doc_path)
        roi_indices = parse_range(page_range, doc.page_count)
        tmp_doc: fitz.Document = fitz.open()
        if unit != "pt":
            margin = tuple(map(lambda x: convert_length(x, unit, "pt"), margin))
        for page_index in roi_indices:
            page = doc[page_index]
            page_width, page_height = page.rect.width, page.rect.height
            bbox = fitz.Rect(margin[3], margin[0], page_width-margin[1], page_height-margin[2])
            if keep_page_size:
                new_page = tmp_doc.new_page(-1, width=page_width, height=page_height)
                new_page.show_pdf_page(new_page.rect, doc, page_index, clip=bbox)
            else:
                new_page = tmp_doc.new_page(-1, width=bbox[2]-bbox[0], height=bbox[3]-bbox[1])
                new_page.show_pdf_page(new_page.rect, doc, page_index, clip=bbox)
        if output_path is None:
            p = Path(doc_path)
            output_path = str(p.parent / f"{p.stem}-裁剪.pdf")
        tmp_doc.save(output_path, garbage=3, deflate=True)
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
        if h_breakpoints:
            h_breakpoints = [v for v in h_breakpoints if 0 <= v <= 1]
            h_breakpoints = [0] + h_breakpoints + [1]
            h_breakpoints.sort()
        else:
            h_breakpoints = [0., 1.]
        if v_breakpoints:
            v_breakpoints = [v for v in v_breakpoints if 0 <= v <= 1]
            v_breakpoints = [0] + v_breakpoints + [1]
            v_breakpoints.sort()
        else:
            v_breakpoints = [0., 1.]
        for page_index in roi_indices:
            page = doc[page_index]
            page_width, page_height = page.rect.width, page.rect.height
            for i in range(len(h_breakpoints)-1):
                for j in range(len(v_breakpoints)-1):
                    bbox = fitz.Rect(v_breakpoints[j]*page_width, h_breakpoints[i]*page_height, v_breakpoints[j+1]*page_width, h_breakpoints[i+1]*page_height)
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
        if paper_size == "same":
            rect = doc[-1].rect
            width, height = rect.width, rect.height
        else:
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
                logger.debug(page_index)
                page = tmp_doc.new_page(-1, width=width, height=height)
            page.show_pdf_page(r_tab[page_index % batch_size], doc, page_index)
        if output_path is None:
            p = Path(doc_path)
            output_path = str(p.parent / f"{p.stem}-网格组合.pdf")
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

def convert_pdf_to_images(doc_path: str, page_range: str = 'all', output_path: str = None):
    doc: fitz.Document = fitz.open(doc_path)
    p = Path(doc_path)
    if page_range=="all":
        roi_indices = list(range(len(doc)))
    else:
        roi_indices = parse_range(page_range)

    if output_path is None:
        output_dir = p.parent / "PDF转图片"
    else:
        output_dir = Path(output_path)
    output_dir.mkdir(parents=True, exist_ok=True)
    for page_index in roi_indices:
        page: fitz.Page = doc[page_index]
        pix = page.get_pixmap()
        savepath = str(output_dir / f"page-{page.number+1}.png")
        pix.pil_save(savepath, quality=100, dpi=(1800,1800))

def convert_images_to_pdf(input_path: str, output_path: str = None):
    raise NotImplementedError

def create_text_wartmark(
        wm_text:str,
        width: Union[int, float],
        height: Union[int, float],
        font: str = "msyh.ttc",
        fontsize: int = 55,
        angle: Union[int, float] = 45,
        text_stroke_color_rgb: Tuple[int, int, int] = (0, 1, 0),
        text_fill_color_rgb: Tuple[int, int, int] = (1, 0, 0),
        text_fill_alpha: Union[int, float] = 0.3,
        num_lines: Union[int, float] = 1,
        line_spacing: Union[int, float] = 2,
        word_spacing: Union[int, float] = 2,
        x_offset: Union[int, float] = 0,
        y_offset: Union[int, float] = 0,
        multiple_mode: bool = False,
        output_path:str = None,
    ) -> None:
    if output_path is None:
        output_path = "watermark.pdf"
    c = canvas.Canvas(output_path,pagesize=(width,height))
    pdfmetrics.registerFont(TTFont('custom_font',font))

    parts = wm_text.split("\n")
    max_part = max(parts, key=lambda x: len(x))
    wm_length = c.stringWidth(max_part, "custom_font", fontsize)
    font_length = c.stringWidth("中", "custom_font", fontsize)
    line_height = c.stringWidth(max_part[0], "custom_font", fontsize)*1.1
    wm_height = line_height * len(parts)
    
    c.setFont("custom_font", fontsize)
    c.setStrokeColorRGB(*text_stroke_color_rgb)
    c.setFillColorRGB(*text_fill_color_rgb)
    c.setFillAlpha(text_fill_alpha)
    c.translate(width/2, height/2)
    c.rotate(angle)

    diagonal_length = math.sqrt(width**2 + height**2) # diagonal length of the paper
    if multiple_mode:
        start_y_list = list(map(lambda x: x*wm_height*(line_spacing+1), range(num_lines)))
        center_y = sum(start_y_list) / len(start_y_list)
        start_y_list = list(map(lambda x: x - center_y + y_offset, start_y_list))
        logger.debug(start_y_list)
        for start_y in start_y_list:
            start_x = -diagonal_length + x_offset
            while start_x < diagonal_length:
                for i, part in enumerate(parts):
                    c.drawString(start_x,start_y-i*line_height,part)
                start_x += wm_length+font_length*word_spacing
    else:
        start_x = - wm_length/2 + x_offset
        start_y = - wm_height/2 + y_offset
        for i, part in enumerate(parts):
            c.drawString(start_x,start_y-i*line_height,part)
    c.save()

def create_image_wartmark(
        width: Union[int, float],
        height: Union[int, float],
        wm_image_path: str,
        angle: Union[int, float] = 0,
        scale: Union[int, float] = 1,
        opacity: Union[int, float] = 1,
        num_lines: Union[int, float] = 1,
        word_spacing: Union[int, float] = 0.1,
        line_spacing: Union[int, float] = 2,
        x_offset: Union[int, float] = 0,
        y_offset: Union[int, float] = 0,
        multiple_mode: bool = False,
        output_path: str = None,
    ):
    try:
        if output_path is None:
            output_path = "watermark.pdf"
        c = canvas.Canvas(output_path,pagesize=(width, height))
        diagonal_length = math.sqrt(width**2 + height**2) # diagonal length of the paper
        wm_image = Image.open(wm_image_path)
        # if opacity:
        alpha = Image.new("L", wm_image.size, int(255*opacity))
        wm_image.putalpha(alpha)
        wm_path = str(Path(output_path).parent / "tmp_wm.png")
        wm_image.save(wm_path)
        logger.debug(wm_path)
        # else:
        #     wm_path = wm_image_path
        logger.debug(wm_image.size)
        wm_width, wm_height = wm_image.size[0]*scale, wm_image.size[1]*scale
        gap = word_spacing*wm_width
        c.translate(width/2, height/2)
        c.rotate(angle)
        if multiple_mode:
            start_y_list = list(map(lambda x: x*wm_height*(line_spacing+1), range(num_lines)))
            center_y = sum(start_y_list) / len(start_y_list)
            start_y_list = list(map(lambda x: x - center_y + y_offset, start_y_list))
            logger.debug(start_y_list)
            for start_y in start_y_list:
                start_x = -diagonal_length + x_offset
                while start_x < diagonal_length:
                    c.drawImage(wm_path, start_x, start_y, width=wm_width, height=wm_height)
                    start_x += wm_width + gap
        else:
            start_x = - wm_width/2 + x_offset
            start_y = - wm_height/2 + y_offset
            c.drawImage(wm_path, start_x, start_y, width=wm_width, height=wm_height)
        c.save()
    except:
        raise ValueError(traceback.format_exc())

def watermark_pdf_by_text(doc_path: str, wm_text: str, page_range: str = "all", output_path: str = None, **args):
    try:
        doc = fitz.open(doc_path)
        page = doc[-1]
        p = Path(doc_path)
        tmp_wm_path = str(p.parent / "tmp_wm.pdf")
        create_text_wartmark(wm_text=wm_text, width=page.rect.width, height=page.rect.height, output_path=tmp_wm_path, **args)
        wm_doc = fitz.open(tmp_wm_path)
        writer = fitz.open()
        roi_indices = parse_range(page_range, doc.page_count)
        for i in roi_indices:
            page: fitz.Page = doc[i]
            new_page: fitz.Page = writer.new_page(width=page.rect.width, height=page.rect.height)
            new_page.show_pdf_page(new_page.rect, doc, page.number)
            new_page.show_pdf_page(new_page.rect, wm_doc, 0, overlay=False)
            
        if output_path is None:
            output_path = p.parent / f"{p.stem}-加水印版.pdf"
        writer.save(output_path)
        wm_doc.close()
        doc.close()
        writer.close()
        os.remove(tmp_wm_path)
    except:
        raise ValueError(traceback.format_exc())

def watermark_pdf_by_image(doc_path: str, wm_path: str, page_range: str = "all", output_path: str = None, **args):
    try:
        doc = fitz.open(doc_path)
        page = doc[-1]
        p = Path(doc_path)
        tmp_wm_path = str(p.parent / "tmp_wm.pdf")
        create_image_wartmark(wm_image_path=wm_path, width=page.rect.width, height=page.rect.height, output_path=tmp_wm_path, **args)
        wm_doc = fitz.open(tmp_wm_path)
        writer = fitz.open()
        roi_indices = parse_range(page_range, doc.page_count)
        for i in roi_indices:
            page: fitz.Page = doc[i]
            new_page: fitz.Page = writer.new_page(width=page.rect.width, height=page.rect.height)
            new_page.show_pdf_page(new_page.rect, doc, page.number)
            new_page.show_pdf_page(new_page.rect, wm_doc, 0, overlay=False)
            
        if output_path is None:
            output_path = p.parent / f"{p.stem}-加水印版.pdf"
        writer.save(output_path)
        wm_doc.close()
        doc.close()
        writer.close()
        os.remove(tmp_wm_path)
    except:
        raise ValueError(traceback.format_exc())

def watermark_pdf_by_pdf(doc_path: str, wm_doc_path: str, page_range: str = "all", output_path: str = None):
    try:
        doc = fitz.open(doc_path)
        wm_doc = fitz.open(wm_doc_path)
        writer = fitz.open()
        roi_indices = parse_range(page_range, doc.page_count)
        for i in roi_indices:
            page: fitz.Page = doc[i]
            new_page: fitz.Page = writer.new_page(width=page.rect.width, height=page.rect.height)
            new_page.show_pdf_page(new_page.rect, doc, page.number)
            new_page.show_pdf_page(new_page.rect, wm_doc, 0, overlay=False)
        if output_path is None:
            p = Path(doc_path)
            output_path = p.parent / f"{p.stem}-加水印版.pdf"
        writer.save(output_path)
        wm_doc.close()
        doc.close()
        writer.close()
    except:
        raise ValueError(traceback.format_exc())

def remove_watermark_by_type(doc_path: str, page_range: str = "all", output_path: str = None):
    try:
        new_doc_path = doc_path
        COMPRESS_FLAG = False
        # 判断是否被压缩
        with open(doc_path, "rb") as f:
            reader = PdfReader(f)
            page = reader.pages[-1]
            if page['/Contents'] == {"/Filter": "/FlateDecode"}:
                new_doc_path = str(Path(doc_path).parent / "tmp.pdf")
                result = subprocess.run(["./qpdf/qpdf.exe", "--qdf", "--object-streams=disable", doc_path, new_doc_path], capture_output=True, text=True, creationflags=subprocess.CREATE_NO_WINDOW)
                logger.debug(f"stdout: {result.stdout}")
                logger.debug(f"stderr: {result.stderr}")
                COMPRESS_FLAG = True
            else:
                new_doc_path = doc_path
        doc: fitz.Document = fitz.open(new_doc_path)
        roi_indices = parse_range(page_range, doc.page_count)
        WATERMARK_FLAG = False
        for page_index in roi_indices:
            page: fitz.Page = doc[page_index]
            page.clean_contents()
            xref = page.get_contents()[0]
            cont = bytearray(page.read_contents())
            if cont.find(b"/Subtype/Watermark"):
                WATERMARK_FLAG = True
                while True:
                    i1 = cont.find(b"/Artifact")  # start of definition
                    if i1 < 0: break  # none more left: done
                    i2 = cont.find(b"EMC", i1)  # end of definition
                    cont[i1 : i2+3] = b""  # remove the full definition source "/Artifact ... EMC"
                doc.update_stream(xref, cont)
        if WATERMARK_FLAG:
            if output_path is None:
                p = Path(doc_path)
                output_path = str(p.parent / f"{p.stem}-去水印版.pdf")
            doc.ez_save(output_path)
        else:
            raise ValueError("没有找到水印，请尝试其他方式!")
        doc.close()
        if COMPRESS_FLAG:
            os.remove(new_doc_path)
    except:
        raise ValueError(traceback.format_exc())

def detect_watermark_index_helper(doc_path: str, wm_page_number: int, outpath: str = None):
    try:
        with open(doc_path, "rb") as f:
            reader = PdfReader(f)
            writer = PdfWriter()
            page = reader.pages[wm_page_number]
            logger.debug(page['/Contents'])
            if "/Contents" in page and  isinstance(page['/Contents'], list):
                for i, v in enumerate(page['/Contents']):
                    tmp_reader = PdfReader(f)
                    tmp_page = tmp_reader.pages[wm_page_number]
                    del tmp_page['/Contents'][i]
                    writer.add_page(tmp_page)
                if outpath is None:
                    p = Path(doc_path)
                    outpath = str(p.parent / f"{p.stem}-人工识别水印.pdf")
                with open(outpath, "wb") as f2:
                    writer.write(f2)
            else:
                raise ValueError("没有找到水印，请尝试其他方式!")
    except:
        raise ValueError(traceback.format_exc())

def remove_watermark_by_index(doc_path: str, wm_index: List[int], page_range: str, output_path: str = None):
    try:
        with open(doc_path, "rb") as f:
            reader = PdfReader(f)
            writer = PdfWriter()
            page_count = len(reader.pages)
            roi_indices = parse_range(page_range, len(reader.pages))
            for i in range(len(wm_index)):
                if wm_index[i] < 0:
                    wm_index[i] = page_count + wm_index[i]
            wm_index.sort(reverse=True)
            for page_index in roi_indices:
                page = reader.pages[page_index]
                for i in wm_index:
                    logger.debug(i)
                    del page['/Contents'][i]
                writer.add_page(page)
            if output_path is None:
                p = Path(doc_path)
                outpath = str(p.parent / f"{p.stem}-去水印版.pdf")
            with open(outpath, "wb") as f2:
                writer.write(f2)
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
    watermark_parser.set_defaults(which='watermark')

    watermark_subparsers = watermark_parser.add_subparsers()
    watermark_add_parser= watermark_subparsers.add_parser("add", help="添加水印")
    watermark_add_parser.set_defaults(watermark_which='add')
    watermark_add_parser.add_argument("input_path", type=str, help="pdf文件路径")
    watermark_add_parser.add_argument("--type", type=str, choices=['text', 'image', 'pdf'], default="text", help="水印类型")
    watermark_add_parser.add_argument("--mark-text", type=str, dest="mark_text", help="水印文本")
    watermark_add_parser.add_argument("--font-family", type=str, dest="font_family", help="水印字体路径")
    watermark_add_parser.add_argument("--font-size", type=int, default=50, dest="font_size", help="水印字体大小")
    watermark_add_parser.add_argument("--color", type=str, default="#000000", dest="color", help="水印文本颜色")
    watermark_add_parser.add_argument("--angle", type=int, default=30, dest="angle", help="水印旋转角度")
    watermark_add_parser.add_argument("--opacity", type=float, default=0.3, dest="opacity", help="水印不透明度")
    watermark_add_parser.add_argument("--line-spacing", type=float, default=1, dest="line_spacing", help="水印行间距")
    watermark_add_parser.add_argument("--word-spacing", type=float, default=1, dest="word_spacing", help="相邻水印间距")
    watermark_add_parser.add_argument("--x-offset", type=float, default=0, dest="x_offset", help="水印x轴偏移量")
    watermark_add_parser.add_argument("--y-offset", type=float, default=0, dest="y_offset", help="水印y轴偏移量")
    watermark_add_parser.add_argument("--multiple-mode", action="store_true", dest="multiple_mode", help="多行水印模式")
    watermark_add_parser.add_argument("--num-lines", type=int, default=1, dest="num_lines", help="多行水印行数")
    watermark_add_parser.add_argument("--wm-path", type=str, dest="wm_path", help="水印图片路径")
    watermark_add_parser.add_argument("--scale", type=float, default=1, dest="scale", help="水印图片缩放比例")
    watermark_add_parser.add_argument("--page_range", type=str, default="all", help="页码范围")
    watermark_add_parser.add_argument("-o", "--output", type=str, help="输出文件路径")

    watermark_remove_parser = watermark_subparsers.add_parser("remove", help="删除水印")
    watermark_remove_parser.set_defaults(watermark_which='remove')
    watermark_remove_parser.add_argument("input_path", type=str, help="pdf文件路径")
    watermark_remove_parser.add_argument("--method", type=str, choices=['type', 'index'], default="type", help="删除方式")
    watermark_remove_parser.add_argument("--page_range", type=str, default="all", help="页码范围")
    watermark_remove_parser.add_argument("--wm_index", type=int, nargs="+", help="水印元素所有索引")
    watermark_remove_parser.add_argument("-o", "--output", type=str, help="输出文件路径")

    watermark_detect_parser = watermark_subparsers.add_parser("detect", help="检测水印")
    watermark_detect_parser.set_defaults(watermark_which='detect')
    watermark_detect_parser.add_argument("input_path", type=str, help="pdf文件路径")
    watermark_detect_parser.add_argument("--wm_index", type=int, default=0, help="水印所在页码")
    watermark_detect_parser.add_argument("-o", "--output", type=str, help="输出文件路径")

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
    combine_parser.add_argument("--nrow", type=int, default=1, help="行数")
    combine_parser.add_argument("--ncol", type=int, default=1, help="列数")
    combine_parser.add_argument("--paper_size", type=str, default="A4", help="纸张大小")
    combine_parser.add_argument("--orientation", type=str, choices=['portrait', 'landscape'], default="portrait", help="纸张方向")
    combine_parser.add_argument("-o", "--output", type=str, help="输出文件路径")

    # 裁剪子命令
    crop_parser = sub_parsers.add_parser("crop", help="裁剪", description="裁剪pdf文件")
    crop_parser.set_defaults(which='crop')
    crop_parser.add_argument("--method", type=str, choices=['bbox', 'margin'], default="bbox", help="裁剪模式")
    crop_parser.add_argument("input_path", type=str, help="pdf文件路径")
    crop_parser.add_argument("--page_range", type=str, default="all", help="页码范围")
    crop_parser.add_argument("--bbox", type=float, nargs=4, help="裁剪框")
    crop_parser.add_argument("--margin", type=float, nargs=4, help="裁剪边距")
    crop_parser.add_argument("--keep_size", action="store_true", help="保持裁剪后的尺寸不变")
    crop_parser.add_argument("--unit", type=str, choices=['pt', 'mm', 'cm', 'in'], default="pt", help="单位")
    crop_parser.add_argument("-o", "--output", type=str, help="输出文件路径")

    # 转换子命令
    convert_parser = sub_parsers.add_parser("convert", help="转换", description="转换pdf文件")
    convert_parser.set_defaults(which='convert')
    convert_parser.add_argument("input_path", type=str, help="pdf文件路径")
    convert_parser.add_argument("--page_range", type=str, default="all", help="页码范围")
    convert_parser.add_argument("--source-type", type=str, choices=["pdf", 'png', "jpg", "svg", "docx"], default="pdf", help="源类型")
    convert_parser.add_argument("--target-type", type=str, choices=['png', "svg", "docx"], default="png", help="目标类型")
    convert_parser.add_argument("-o", "--output", type=str, help="输出文件路径")

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
    elif args.which == "combine":
        combine_pdf_by_grid(args.input_path, args.nrow, args.ncol, args.paper_size, args.orientation, args.page_range, args.output)
    elif args.which == "crop":
        if args.method == "bbox":
            crop_pdf_by_bbox(args.input_path, args.bbox, args.unit, args.keep_size, args.page_range, args.output)
        elif args.method == "margin":
            crop_pdf_by_page_margin(args.input_path, args.margin, args.unit, args.keep_size, args.page_range, args.output)
    elif args.which == "convert":
        pass
    elif args.which == "watermark":
        if args.watermark_which == "add":
            if args.type == "text":
                color = hex_to_rgb(args.color)
                watermark_pdf_by_text(doc_path=args.input_path, wm_text=args.mark_text, page_range=args.page_range, output_path=args.output, font=args.font_family, fontsize=args.font_size, angle=args.angle, text_stroke_color_rgb=(0, 0, 0), text_fill_color_rgb=color, text_fill_alpha=args.opacity, num_lines=args.num_lines, line_spacing=args.line_spacing, word_spacing=args.word_spacing, multiple_mode=args.multiple_mode, x_offset=args.x_offset, y_offset=args.y_offset)
            elif args.type == "image":
                watermark_pdf_by_image(doc_path=args.input_path, wm_path=args.wm_path, page_range=args.page_range, output_path=args.output, scale=args.scale, angle=args.angle, opacity=args.opacity, multiple_mode=args.multiple_mode, num_lines=args.num_lines, line_spacing=args.line_spacing, word_spacing=args.word_spacing, x_offset=args.x_offset, y_offset=args.y_offset)
            elif args.type == "pdf":
                watermark_pdf_by_pdf(doc_path=args.input_path, wm_doc_path=args.wm_path, page_range=args.page_range, output_path=args.output)
        elif args.watermark_which == "remove":
            if args.method == "type":
                remove_watermark_by_type(doc_path=args.input_path, page_range=args.page_range, output_path=args.output)
            elif args.method == "index":
                remove_watermark_by_index(doc_path=args.input_path, wm_index=args.wm_index, page_range=args.page_range, output_path=args.output)
        elif args.watermark_which == "detect":
            detect_watermark_index_helper(doc_path=args.input_path, wm_page_number=args.wm_index, outpath=args.output)

if __name__ == "__main__":
    main()
    # create_text_wartmark(
    #     wm_text         = '内部资料',
    #     width           = 200,
    #     height          = 200,
    #     font            = 'msyh.ttc',
    #     fontsize        = 55,
    #     angle           = -90,
    #     text_fill_alpha = 0.3,
    #     num_lines       = 3,
    #     line_spacing    = 1,
    #     multiple_mode   = False,
    #     x_offset        = 0,
    #     y_offset        = 0,
    #     output_path     = r'C:\Users\kevin\Downloads\pdfcpu_0.4.1_Windows_x86_64\水印.pdf',
    # )

    # watermark_pdf_by_text("C:/Users/kevin/Downloads/2023考研英语一真题-去水印版.pdf", "内部资料", output_path=None, num_lines=3, line_spacing=1, multiple_mode=False, x_offset=0, y_offset=0)
    # create_image_wartmark(
    #     595,
    #     842,
    #     r"C:\Users\kevin\miniconda3\envs\ocr\Lib\site-packages\pdf2docx\gui\icon.ico",
    #     scale=0.2,
    #     angle=45,
    #     opacity=0.3,
    #     multiple_mode=True,
    #     num_lines=3,
    #     line_spacing=2,
    #     word_spacing=3
    # )
