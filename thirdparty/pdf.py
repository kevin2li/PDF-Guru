import argparse
import colorsys
import glob
import json
import math
import os
import re
import shutil
import subprocess
import traceback
from pathlib import Path
from typing import List, Tuple, Union

import fitz
from loguru import logger
from PIL import Image
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.pdfgen import canvas

logger.add("pdf.log", rotation="1 week", retention="10 days", level="DEBUG", encoding="utf-8")
cmd_output_path = "cmd_output.json"

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

def dump_json(path, obj):
    with open(path, "w", encoding="utf-8") as f:
        json.dump(obj, f, ensure_ascii=False)

def convert_length(length, from_unit, to_unit):
    """
    将长度从一个单位转换为另一个单位
    :param length: 长度值
    :param from_unit: 原单位，可选值："pt"、"cm"、"mm"、"in"
    :param to_unit: 目标单位，可选值："pt"、"cm"、"mm"、"in"
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

# 阿拉伯数字转罗马数字
def num_to_roman(num):
    roman_map = {1: 'I', 4: 'IV', 5: 'V', 9: 'IX', 10: 'X', 40: 'XL', 50: 'L', 90: 'XC', 100: 'C', 400: 'CD', 500: 'D', 900: 'CM', 1000: 'M'}
    result = ''
    for value, symbol in sorted(roman_map.items(), reverse=True):
        while num >= value:
            result += symbol
            num -= value
    return result

# 将阿拉伯数字转换为字母表
def num_to_letter(num):
    if num <= 0:
        return ""
    # 将数字转换为 0-25 的范围
    num -= 1
    quotient, remainder = divmod(num, 26)
    # 递归转换前面的部分
    prefix = num_to_letter(quotient)
    # 将当前位转换为字母
    letter = chr(ord('A') + remainder)
    # 拼接前缀和当前字母
    return prefix + letter


def num_to_chinese(num):
    """将阿拉伯数字转换为中文数字"""
    CHINESE_NUMBERS = {
        0: "零", 1: "一", 2: "二", 3: "三", 4: "四", 5: "五",
        6: "六", 7: "七", 8: "八", 9: "九", 10: "十"
    }
    if num == 0:
        return CHINESE_NUMBERS[num]

    result = ""
    if num >= 100000000:  # 亿
        quotient, remainder = divmod(num, 100000000)
        result += num_to_chinese(quotient) + "亿"
        num = remainder

    if num >= 10000:  # 万
        quotient, remainder = divmod(num, 10000)
        result += num_to_chinese(quotient) + "万"
        num = remainder

    if num >= 1000:  # 千
        quotient, remainder = divmod(num, 1000)
        result += CHINESE_NUMBERS[quotient] + "千"
        num = remainder

    if num >= 100:  # 百
        quotient, remainder = divmod(num, 100)
        result += CHINESE_NUMBERS[quotient] + "百"
        num = remainder

    if num >= 10:  # 十
        quotient, remainder = divmod(num, 10)
        if quotient > 1:
            result += CHINESE_NUMBERS[quotient]
        result += "十"
        num = remainder

    if num > 0:
        result += CHINESE_NUMBERS[num]

    return result

def human_readable_size(size):
    """将文件大小转换为适合人类阅读的格式"""
    for unit in ["B", "KB", "MB", "GB", "TB"]:
        if size < 1024.0:
            return f"{size:.2f} {unit}"
        size /= 1024.0
    return f"{size:.2f} PB"

def batch_process(func):
    def wrapper(*args, **kwargs):
        logger.debug(args)
        logger.debug(kwargs)
        doc_path = kwargs['doc_path']
        if "*" in doc_path:
            path_list = glob.glob(doc_path)
            logger.debug(f"path_list length: {len(path_list) if path_list else 0}")
            if path_list:
                for path in path_list:
                    kwargs["doc_path"] = path
                    func(*args, **kwargs)
        else:
            func(*args, **kwargs)
        func(*args, **kwargs)
    return wrapper

# 功能类函数
@batch_process
def slice_pdf(doc_path: str, page_range: str = "all", output_path: str = None, is_reverse: bool = False):
    try:
        doc: fitz.Document = fitz.open(doc_path)
        p = Path(doc_path)
        if output_path is None:
            output_dir = p.parent
        roi_indices = parse_range(page_range, doc.page_count, is_reverse=is_reverse)
        writer: fitz.Document = fitz.open()
        parts = range_compress(roi_indices)
        for part in parts:
            writer.insert_pdf(doc, from_page=part[0], to_page=part[1])
        writer.save(str(output_dir / f"{p.stem}-切片.pdf"), garbage=3, deflate=True)
        dump_json(cmd_output_path, {"status": "success", "message": ""})
    except:
        logger.error(f"roi_indices: {roi_indices}")
        logger.error(traceback.format_exc())
        dump_json(cmd_output_path, {"status": "error", "message": traceback.format_exc()})

@batch_process
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
            writer:fitz.Document = fitz.open()
            writer.insert_pdf(doc, from_page=i, to_page=min(i+chunk_size, doc.page_count)-1)
            writer.save(savepath, garbage=3, deflate=True)
        dump_json(cmd_output_path, {"status": "success", "message": ""})
    except:
        logger.error(traceback.format_exc())
        dump_json(cmd_output_path, {"status": "error", "message": traceback.format_exc()})

@batch_process
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
            writer: fitz.Document = fitz.open()
            parts = range_compress(indices)
            for part in parts:
                writer.insert_pdf(doc, from_page=part[0], to_page=part[1])
            writer.save(str(output_dir / f"{p.stem}-part{i}.pdf"), garbage=3, deflate=True)
        dump_json(cmd_output_path, {"status": "success", "message": ""})
    except:
        logger.error(traceback.format_exc())
        dump_json(cmd_output_path, {"status": "error", "message": traceback.format_exc()})

@batch_process
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
            writer: fitz.Document = fitz.open()
            writer.insert_pdf(doc, from_page=begin, to_page=end)
            title = p[1][1].replace("/", "-").replace("\\", "-").replace(":", "-").replace("?","-").replace("*", "-").replace("\"", "-").replace("<", "-").replace(">", "-").replace("|", "-")

            tmp_toc = list(map(lambda x: [x[0], x[1], x[2]-begin],toc[cur_idx:next_idx]))
            writer.set_toc(tmp_toc)
            writer.save(str(output_dir / f"{title}.pdf"), garbage=3, deflate=True)
        dump_json(cmd_output_path, {"status": "success", "message": ""})
    except:
        logger.error(traceback.format_exc())
        dump_json(cmd_output_path, {"status": "error", "message": traceback.format_exc()})

@batch_process
def reorder_pdf(doc_path: str, page_range: str = "all", output_path: str = None):
    try:
        doc: fitz.Document = fitz.open(doc_path)
        p = Path(doc_path)
        roi_indices = parse_range(page_range, doc.page_count, is_unique=False)
        if output_path is None:
            output_path = str(p.parent / f"{p.stem}-重排.pdf")
        writer: fitz.Document = fitz.open()
        for i in roi_indices:
            writer.insert_pdf(doc, from_page=i, to_page=i)
        writer.save(output_path, garbage=3, deflate=True)
        dump_json(cmd_output_path, {"status": "success", "message": ""})
    except:
        logger.error(traceback.format_exc())
        dump_json(cmd_output_path, {"status": "error", "message": traceback.format_exc()})

@batch_process
def insert_blank_pdf(doc_path: str, pos: int, pos_type: str, count: int, orientation: str, paper_size: str, output_path: str = None):
    try:
        doc: fitz.Document = fitz.open(doc_path)
        p = Path(doc_path)
        if output_path is None:
            output_path = str(p.parent / f"{p.stem}-插入空白页.pdf")
        writer: fitz.Document = fitz.open()
        if paper_size == "same":
            fmt = doc[0].rect
        else:
            fmt = fitz.paper_rect(f"{paper_size}-l") if orientation == "landscape" else fitz.paper_rect(paper_size)

        if pos_type == 'before_first':
            pos = 1
        elif pos_type == 'after_first':
            pos = 2
        elif pos_type == 'before_last':
            pos = doc.page_count
        elif pos_type == 'after_last':
            pos = doc.page_count+1
        elif pos_type == 'before_custom':
            pass
        elif pos_type == 'after_custom':
            pos = pos + 1
        if pos - 2 >= 0:
            writer.insert_pdf(doc, from_page=0, to_page=pos-2)
        for i in range(count):
            writer.new_page(-1, width=fmt.width, height=fmt.height)
        if pos-1 < doc.page_count:
            writer.insert_pdf(doc, from_page=pos-1, to_page=-1)
        writer.save(output_path, garbage=3, deflate=True)
        dump_json(cmd_output_path, {"status": "success", "message": ""})
    except:
        logger.error(traceback.format_exc())
        dump_json(cmd_output_path, {"status": "error", "message": traceback.format_exc()})

def insert_pdf(doc_path1: str, doc_path2: str, insert_pos: int, pos_type: str, page_range: str = "all", output_path: str = None):
    try:
        doc1: fitz.Document = fitz.open(doc_path1)
        doc2: fitz.Document = fitz.open(doc_path2)
        page_range = page_range.strip()
        assert 1 <= insert_pos <= doc1.page_count, "插入位置超出范围!"
        n1, n2 = doc1.page_count, doc2.page_count
        if output_path is None:
            p = Path(doc_path1)
            output_path = str(p.parent / f"{p.stem}-插入.pdf")
        writer: fitz.Document = fitz.open()
        
        if pos_type == 'before_first':
            insert_pos = 1
        elif pos_type == 'after_first':
            insert_pos = 2
        elif pos_type == 'before_last':
            insert_pos = doc1.page_count
        elif pos_type == 'after_last':
            insert_pos = doc1.page_count+1
        elif pos_type == 'before_custom':
            pass
        elif pos_type == 'after_custom':
            insert_pos = insert_pos + 1

        if insert_pos - 2 >= 0:
            writer.insert_pdf(doc1, from_page=0, to_page=insert_pos-2)
        doc2_indices = parse_range(page_range, n2)
        for i in doc2_indices:
            writer.insert_pdf(doc2, from_page=i, to_page=i)
        if insert_pos-1 < n1:
            writer.insert_pdf(doc1, from_page=insert_pos-1, to_page=n1-1)
        writer.save(output_path, garbage=3, deflate=True)
        dump_json(cmd_output_path, {"status": "success", "message": ""})
    except:
        logger.error(traceback.format_exc())
        dump_json(cmd_output_path, {"status": "error", "message": traceback.format_exc()})

def replace_pdf(doc_path1: str, doc_path2: str, src_range: str = "all", dst_range: str = "all", output_path: str = None):
    try:
        doc1: fitz.Document = fitz.open(doc_path1)
        doc2: fitz.Document = fitz.open(doc_path2)
        src_range = src_range.strip()
        dst_range = dst_range.strip()
        n1, n2 = doc1.page_count, doc2.page_count
        if re.match("^!?(\d+|N)(\-(\d+|N))?$", src_range) is None:
            logger.error(f"src_range: {src_range}, 源页码格式错误")
            dump_json(cmd_output_path, {"status": "error", "message": "源页码格式错误!"})
            return
        if output_path is None:
            p = Path(doc_path1)
            output_path = str(p.parent / f"{p.stem}-替换.pdf")
        writer: fitz.Document = fitz.open()
        dst_indices = parse_range(dst_range, n2)
        parts = src_range.split("-")
        if len(parts) == 2:
            a, b = parts
            a = int(a) if a != "N" else n1
            b = int(b) if b != "N" else n1
            if a-2 >= 0:
                writer.insert_pdf(doc1, from_page=0, to_page=a-2)
            for i in dst_indices:
                writer.insert_pdf(doc2, from_page=i, to_page=i)
            writer.insert_pdf(doc1, from_page=b, to_page=n1-1)
            writer.save(output_path, garbage=3, deflate=True)
        elif len(parts) == 1:
            a = int(parts[0]) if parts[0] != "N" else n1
            if a-2 >= 0:
                writer.insert_pdf(doc1, from_page=0, to_page=a-2)
            for i in dst_indices:
                writer.insert_pdf(doc2, from_page=i, to_page=i)
            if a < n1:
                writer.insert_pdf(doc1, from_page=a, to_page=n1-1)
            writer.save(output_path, garbage=3, deflate=True)
        else:
            logger.error("页码格式错误")
            dump_json(cmd_output_path, {"status": "error", "message": "页码格式错误!"})
            return
        dump_json(cmd_output_path, {"status": "success", "message": ""})
    except:
        logger.error(traceback.format_exc())
        dump_json(cmd_output_path, {"status": "error", "message": traceback.format_exc()})

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
        elif sort_method == "name_digit":
            new_path_list = sorted(new_path_list, key=lambda x: int(re.search(r"\d+$", Path(x).stem).group()))
            if sort_direction == "asc":
                pass
            else:
                new_path_list = new_path_list[::-1]
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
        writer: fitz.Document = fitz.open()
        toc_list = []
        cur_page_number = 0
        for doc_path in new_path_list:
            doc_temp = fitz.open(doc_path)
            toc_temp = doc_temp.get_toc(simple=True)
            if toc_temp:
                toc_temp = list(map(lambda x: [x[0], x[1], x[2]+cur_page_number], toc_temp))
            else:
                toc_temp = [[1, Path(doc_path).stem, cur_page_number+1]]
            toc_list.extend(toc_temp)
            cur_page_number += doc_temp.page_count
            writer.insert_pdf(doc_temp)
        writer.set_toc(toc_list)
        if output_path is None:
            p = Path(doc_path_list[0])
            output_path = str(p.parent / f"{p.stem}(等)合并.pdf").replace("*", "")
        writer.save(output_path, garbage=3, deflate=True)
        dump_json(cmd_output_path, {"status": "success", "message": ""})
    except:
        logger.error(traceback.format_exc())
        dump_json(cmd_output_path, {"status": "error", "message": traceback.format_exc()})

@batch_process
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
        doc.save(output_path, garbage=3, deflate=True)
        dump_json(cmd_output_path, {"status": "success", "message": ""})
    except:
        logger.error(traceback.format_exc())
        dump_json(cmd_output_path, {"status": "error", "message": traceback.format_exc()})

@batch_process
def crop_pdf_by_bbox(doc_path: str, bbox: Tuple[int, int, int, int], unit: str = "pt", keep_page_size: bool = True, page_range: str = "all", output_path: str = None):
    try:
        doc: fitz.Document = fitz.open(doc_path)
        roi_indices = parse_range(page_range, doc.page_count)
        writer: fitz.Document = fitz.open()
        if unit != "pt":
            bbox = tuple(map(lambda x: convert_length(x, unit, "pt"), bbox))
            logger.debug(bbox)
        for page_index in roi_indices:
            page = doc[page_index]
            page_width, page_height = page.rect.width, page.rect.height
            if keep_page_size:
                new_page = writer.new_page(-1, width=page_width, height=page_height)
                new_page.show_pdf_page(new_page.rect, doc, page_index, clip=bbox)
            else:
                new_page = writer.new_page(-1, width=bbox[2]-bbox[0], height=bbox[3]-bbox[1])
                new_page.show_pdf_page(new_page.rect, doc, page_index, clip=bbox)
        if output_path is None:
            p = Path(doc_path)
            output_path = str(p.parent / f"{p.stem}-裁剪.pdf")
        writer.save(output_path, garbage=3, deflate=True)
        dump_json(cmd_output_path, {"status": "success", "message": ""})
    except:
        logger.error(traceback.format_exc())
        dump_json(cmd_output_path, {"status": "error", "message": traceback.format_exc()})

@batch_process
def crop_pdf_by_page_margin(doc_path: str, margin: Tuple[int, int, int, int], unit: str = "pt", keep_page_size: bool = True, page_range: str = "all", output_path: str = None):
    try:
        doc: fitz.Document = fitz.open(doc_path)
        roi_indices = parse_range(page_range, doc.page_count)
        writer: fitz.Document = fitz.open()
        if unit != "pt":
            margin = tuple(map(lambda x: convert_length(x, unit, "pt"), margin))
        for page_index in roi_indices:
            page = doc[page_index]
            page_width, page_height = page.rect.width, page.rect.height
            bbox = fitz.Rect(margin[3], margin[0], page_width-margin[1], page_height-margin[2])
            if keep_page_size:
                new_page = writer.new_page(-1, width=page_width, height=page_height)
                new_page.show_pdf_page(new_page.rect, doc, page_index, clip=bbox)
            else:
                new_page = writer.new_page(-1, width=bbox[2]-bbox[0], height=bbox[3]-bbox[1])
                new_page.show_pdf_page(new_page.rect, doc, page_index, clip=bbox)
        if output_path is None:
            p = Path(doc_path)
            output_path = str(p.parent / f"{p.stem}-裁剪.pdf")
        writer.save(output_path, garbage=3, deflate=True)
        dump_json(cmd_output_path, {"status": "success", "message": ""})
    except:
        logger.error(traceback.format_exc())
        dump_json(cmd_output_path, {"status": "error", "message": traceback.format_exc()})

@batch_process
def cut_pdf_by_grid(doc_path: str, n_row: int, n_col: int, page_range: str = "all", output_path: str = None):
    try:
        doc: fitz.Document = fitz.open(doc_path)
        roi_indices = parse_range(page_range, doc.page_count)
        writer: fitz.Document = fitz.open()
        for page_index in roi_indices:
            page = doc[page_index]
            page_width, page_height = page.rect.width, page.rect.height
            width, height = page_width/n_col, page_height/n_row
            for i in range(n_row):
                for j in range(n_col):
                    bbox = fitz.Rect(j*width, i*height, (j+1)*width, (i+1)*height)
                    # bbox += d
                    tmp_page = writer.new_page(-1, width=bbox.width, height=bbox.height)
                    tmp_page.show_pdf_page(tmp_page.rect, doc, page_index, clip=bbox)
        if output_path is None:
            p = Path(doc_path)
            output_path = str(p.parent / f"{p.stem}-网格分割.pdf")
        writer.save(output_path, garbage=3, deflate=True)
        dump_json(cmd_output_path, {"status": "success", "message": ""})
    except:
        logger.error(traceback.format_exc())
        dump_json(cmd_output_path, {"status": "error", "message": traceback.format_exc()})

@batch_process
def cut_pdf_by_breakpoints(doc_path: str, h_breakpoints: List[float], v_breakpoints: List[float], page_range: str = "all", output_path: str = None):
    try:
        doc: fitz.Document = fitz.open(doc_path)
        roi_indices = parse_range(page_range, doc.page_count)
        writer: fitz.Document = fitz.open()
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
                    new_page = writer.new_page(-1, width=bbox.width, height=bbox.height)
                    new_page.show_pdf_page(new_page.rect, doc, page_index, clip=bbox)
        if output_path is None:
            p = Path(doc_path)
            output_path = str(p.parent / f"{p.stem}-自定义分割.pdf")
        writer.save(output_path, garbage=3, deflate=True)
        dump_json(cmd_output_path, {"status": "success", "message": ""})
    except:
        logger.error(traceback.format_exc())
        dump_json(cmd_output_path, {"status": "error", "message": traceback.format_exc()})

@batch_process
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
        writer: fitz.Document = fitz.open()
        roi_indices = parse_range(page_range, doc.page_count)
        for page_index in roi_indices:
            if page_index % batch_size == 0:
                logger.debug(page_index)
                page = writer.new_page(-1, width=width, height=height)
            page.show_pdf_page(r_tab[page_index % batch_size], doc, page_index)
        if output_path is None:
            p = Path(doc_path)
            output_path = str(p.parent / f"{p.stem}-网格组合.pdf")
        writer.save(output_path, garbage=3, deflate=True)
        dump_json(cmd_output_path, {"status": "success", "message": ""})
    except:
        logger.error(traceback.format_exc())
        dump_json(cmd_output_path, {"status": "error", "message": traceback.format_exc()})

@batch_process
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
        dump_json(cmd_output_path, {"status": "success", "message": ""})
    except:
        logger.error(traceback.format_exc())
        dump_json(cmd_output_path, {"status": "error", "message": traceback.format_exc()})

@batch_process
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
        dump_json(cmd_output_path, {"status": "success", "message": ""})
    except:
        logger.error(traceback.format_exc())
        dump_json(cmd_output_path, {"status": "error", "message": traceback.format_exc()})

def title_preprocess(title: str, rules: List[dict] = None):
    """提取标题层级和标题内容
    """
    try:
        title = title.rstrip()
        res = {}
        # 优先根据rule匹配
        if rules:
            for rule in rules:
                if rule['type'] != "custom":
                    if rule['prefix'] in ["1", "1."]:
                        m = re.match("\s*(\d+\.?)\s+(.+)", title)
                        if m is not None:
                            res['text'] = f"{m.group(1)} {m.group(2)}"
                            res['level'] = int(rule["level"])
                            return res
                    elif rule["prefix"] == "1.1":
                        m = re.match("\s*(\d+\.\d+\.?)\s+(.+)", title)
                        if m is not None:
                            res['text'] = f"{m.group(1)} {m.group(2)}"
                            res['level'] = int(rule["level"])
                            return res
                    elif rule["prefix"] == "1.1.1":
                        m = re.match("\s*(\d+\.\d+\.\d+\.?)\s+(.+)", title)
                        if m is not None:
                            res['text'] = f"{m.group(1)} {m.group(2)}"
                            res['level'] = int(rule["level"])
                            return res
                    elif rule["prefix"] == "1.1.1.1":
                        m = re.match("\s*(\d+\.\d+\.\d+\.\d+\.?)\s+(.+)", title)
                        if m is not None:
                            res['text'] = f"{m.group(1)} {m.group(2)}"
                            res['level'] = int(rule["level"])
                            return res
                    elif rule["prefix"] in ["第一章", "第一节", "第一小节", "第一卷", "第一编", "第一部分", "第一课"]:
                        m = re.match("\s*(第.+[章|节|编|卷|部分|课])\s*(.+)", title)
                        if m is not None:
                            res['text'] = f"{m.group(1)} {m.group(2)}"
                            res['level'] = int(rule["level"])
                            return res
                    elif rule["prefix"] in ["Chapter 1", "Lesson 1"]:
                        m = re.match("\s*((Chapter|Lesson) \d+\.?)\s*(.+)", title)
                        if m is not None:
                            res['text'] = f"{m.group(1)} {m.group(2)}"
                            res['level'] = int(rule["level"])
                            return res
                    elif rule["prefix"] in ["一、", "一."]:
                        m = re.match("\s*([一二三四五六七八九十]+[、.])\s*(.+)", title)
                        if m is not None:
                            res['text'] = f"{m.group(1)} {m.group(2)}"
                            res['level'] = int(rule["level"])
                            return res
                else:
                    m = re.match(f'\s*({rule["prefix"]})\s+(.+)', title)
                    if m is not None:
                        res['text'] = f"{m.group(1)} {m.group(2)}"
                        res['level'] = int(rule["level"])
                        return res
        # 其次根据缩进匹配
        if title.startswith("\t"):
            m = re.match("(\t*)\s*(.+)", title)
            res['text'] = f"{m.group(2)}".rstrip()
            res['level'] = len(m.group(1))+1
            return res
        
        # 无匹配
        res['text'] = title
        res['level'] = 1
        return res
    except:
        return {'level': 1, "text": title}

@batch_process
def add_toc_from_file(toc_path: str, doc_path: str, offset: int, output_path: str = None):
    """从目录文件中导入书签到pdf文件(若文件中存在行没指定页码则按1算)

    Args:
        toc_path (str): 目录文件路径
        doc_path (str): pdf文件路径
        offset (int): 偏移量, 计算方式: “pdf文件实际页码” - “目录文件标注页码”
    """
    try:
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
            logger.error("不支持的toc文件格式!")
            dump_json(cmd_output_path, "不支持的toc文件格式!")
            return
        # 校正层级
        levels = [v[0] for v in toc]
        diff = [levels[i+1]-levels[i] for i in range(len(levels)-1)]
        indices = [i for i in range(len(diff)) if diff[i] > 1]
        for idx in indices:
            toc[idx][0] = toc[idx+1][0]
        logger.debug(toc)
        doc.set_toc(toc)
        if output_path is None:
            output_path = str(p.parent / f"{p.stem}-加书签目录.pdf")
        doc.save(output_path, garbage=3, deflate=True)
        dump_json(cmd_output_path, {"status": "success", "message": ""})
    except:
        logger.error(traceback.format_exc())
        dump_json(cmd_output_path, {"status": "error", "message": traceback.format_exc()})

@batch_process
def add_toc_by_gap(doc_path: str, gap: int = 1, format: str = "第%p页", output_path: str = None):
    try:
        doc: fitz.Document = fitz.open(doc_path)
        p = Path(doc_path)
        toc = []
        for i in range(0, doc.page_count, gap):
            toc.append([1, format.replace("%p", str(i+1)), i+1])
        toc.append([1, format.replace("%p", str(doc.page_count)), doc.page_count])
        doc.set_toc(toc)
        if output_path is None:
            output_path = str(p.parent / f"{p.stem}-[页码书签版].pdf")
        doc.save(output_path, garbage=3, deflate=True)
        dump_json(cmd_output_path, {"status": "success", "message": ""})
    except:
        logger.error(traceback.format_exc())
        dump_json(cmd_output_path, {"status": "error", "message": traceback.format_exc()})

@batch_process
def extract_toc(doc_path: str, format: str = "txt", output_path: str = None):
    try:
        doc: fitz.Document = fitz.open(doc_path)
        p = Path(doc_path)
        toc = doc.get_toc(simple=False)
        if not toc:
            dump_json(cmd_output_path, {"status": "error", "message": "该文件没有书签!"})
            return
        if format == "txt":
            if output_path is None:
                output_path = str(p.parent / f"{p.stem}-书签.txt")
            with open(output_path, "w", encoding="utf-8") as f:
                for line in toc:
                    indent = (line[0]-1)*"\t"
                    f.writelines(f"{indent}{line[1]} {line[2]}\n")
        elif format == "json":
            if output_path is None:
                output_path = str(p.parent / f"{p.stem}-书签.json")
            for i in range(len(toc)):
                try:
                    toc[i][-1] = toc[i][-1]['to'].y
                except:
                    toc[i][-1] = 0
            with open(output_path, "w", encoding="utf-8") as f:
                json.dump(toc, f)
        dump_json(cmd_output_path, {"status": "success", "message": ""})
    except:
        logger.error(traceback.format_exc())
        dump_json(cmd_output_path, {"status": "error", "message": traceback.format_exc()})

def transform_toc_file(toc_path: str, level_dict_list: List[dict] = None, add_offset: int = 0, delete_level_below: int = None, default_level: int = 1, is_remove_blanklines: bool = True, output_path: str = None):
    try:
        logger.debug(level_dict_list)
        if output_path is None:
            p = Path(toc_path)
            output_path = str(p.parent / f"{p.stem}-书签转换.txt")
        with open(toc_path, "r", encoding="utf-8") as f, open(output_path, "w", encoding="utf-8") as f2:
            for line in f:
                if not line.strip(): # 空行
                    if is_remove_blanklines:
                        continue
                    else:
                        f2.write(f"{line}\n")
                        continue
                old_line = line
                new_line = line
                if add_offset:
                    m = re.search("(\d+)(?=\s*$)", new_line)
                    if m is not None:
                        pno = int(m.group(1))
                        pno = pno + add_offset
                        new_line = new_line[:m.span()[0]-1] + f" {pno}\n"
                        old_line = new_line # 页码更新不算
                if level_dict_list:
                    out = title_preprocess(new_line, level_dict_list)
                    new_line = "\t"*(out['level']-1) + out['text'] + "\n"
                if delete_level_below:
                    if new_line.startswith("\t"*(delete_level_below-1)):
                        continue
                if new_line == old_line: # 没有发生变化
                    new_line = "\t"*(default_level-1) + old_line
                f2.write(new_line)
            f2.flush()
        dump_json(cmd_output_path, {"status": "success", "message": ""})
    except:
        logger.error(traceback.format_exc())
        dump_json(cmd_output_path, {"status": "error", "message": traceback.format_exc()})

@batch_process
def encrypt_pdf(doc_path: str, user_password: str, owner_password: str = None, perm: List[str] = [], output_path: str = None):
    try:
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
            garbage=3,
            deflate=True,
        )
        dump_json(cmd_output_path, {"status": "success", "message": ""})
    except:
        logger.error(traceback.format_exc())
        dump_json(cmd_output_path, {"status": "error", "message": traceback.format_exc()})

@batch_process
def decrypt_pdf(doc_path: str, password: str, output_path: str = None):
    try:
        doc: fitz.Document = fitz.open(doc_path)
        p = Path(doc_path)
        if doc.isEncrypted:
            doc.authenticate(password)
            n = doc.page_count
            doc.select(range(n))
        if output_path is None:
            output_path = str(p.parent / f"{p.stem}-解密.pdf")
        doc.save(output_path, garbage=3, deflate=True)
        dump_json(cmd_output_path, {"status": "success", "message": ""})
    except:
        logger.error(traceback.format_exc())
        dump_json(cmd_output_path, {"status": "error", "message": traceback.format_exc()})

@batch_process
def compress_pdf(doc_path: str, output_path: str = None):
    try:
        doc: fitz.Document = fitz.open(doc_path)
        p = Path(doc_path)
        if output_path is None:
            output_path = str(p.parent / f"{p.stem}-压缩.pdf")
        doc.save(output_path, garbage=4, deflate=True, clean=True)
        dump_json(cmd_output_path, {"status": "success", "message": ""})
    except:
        logger.error(traceback.format_exc())
        dump_json(cmd_output_path, {"status": "error", "message": traceback.format_exc()})

@batch_process
def resize_pdf_by_dim(doc_path: str, width: float, height: float, unit: str = "pt", page_range: str = "all", output_path: str = None):
    try:
        doc: fitz.Document = fitz.open(doc_path)
        writer: fitz.Document = fitz.open()
        width, height = convert_length(width, unit, "pt"), convert_length(height, unit, "pt")
        roi_indices = parse_range(page_range, doc.page_count)
        for i in range(doc.page_count):
            if i not in roi_indices:
                writer.insert_pdf(doc, from_page=i, to_page=i)
                continue
            page = doc[i]
            new_page: fitz.Page = writer.new_page(width=width, height=height)
            new_page.show_pdf_page(new_page.rect, doc, page.number, rotate=page.rotation)
        p = Path(doc_path)
        if output_path is None:
            output_path = str(p.parent / f"{p.stem}-缩放.pdf")
        writer.save(output_path, garbage=3, deflate=True)
        dump_json(cmd_output_path, {"status": "success", "message": ""})
    except:
        logger.error(traceback.format_exc())
        dump_json(cmd_output_path, {"status": "error", "message": traceback.format_exc()})

@batch_process
def resize_pdf_by_scale(doc_path: str, scale: float, page_range: str = "all", output_path: str = None):
    try:
        doc: fitz.Document = fitz.open(doc_path)
        writer: fitz.Document = fitz.open()
        roi_indices = parse_range(page_range, doc.page_count)
        for i in range(doc.page_count):
            if i not in roi_indices:
                writer.insert_pdf(doc, from_page=i, to_page=i)
                continue
            page = doc[i]
            new_page: fitz.Page = writer.new_page(width=page.rect.width*scale, height=page.rect.height*scale)
            new_page.show_pdf_page(new_page.rect, doc, page.number, rotate=page.rotation)
        if output_path is None:
            p = Path(doc_path)
            output_path = str(p.parent / f"{p.stem}-缩放.pdf")
        writer.save(output_path, garbage=3, deflate=True)
        dump_json(cmd_output_path, {"status": "success", "message": ""})
    except:
        logger.error(traceback.format_exc())
        dump_json(cmd_output_path, {"status": "error", "message": traceback.format_exc()})

@batch_process
def resize_pdf_by_paper_size(doc_path: str, paper_size: str, page_range: str = "all", output_path: str = None):
    try:
        doc: fitz.Document = fitz.open(doc_path)
        writer: fitz.Document = fitz.open()
        roi_indices = parse_range(page_range, doc.page_count)
        for i in range(doc.page_count):
            if i not in roi_indices:
                writer.insert_pdf(doc, from_page=i, to_page=i)
                continue
            page = doc[i]
            if page.rect.width > page.rect.height:
                fmt = fitz.paper_rect(f"{paper_size}-l")
            else:
                fmt = fitz.paper_rect(f"{paper_size}")
            new_page: fitz.Page = writer.new_page(width=fmt.width, height=fmt.height)
            new_page.show_pdf_page(new_page.rect, doc, page.number, rotate=page.rotation)
        if output_path is None:
            p = Path(doc_path)
            output_path = str(p.parent / f"{p.stem}-缩放.pdf")
        writer.save(output_path, garbage=3, deflate=True)
        dump_json(cmd_output_path, {"status": "success", "message": ""})
    except:
        logger.error(traceback.format_exc())
        dump_json(cmd_output_path, {"status": "error", "message": traceback.format_exc()})

def create_text_wartmark(
        wm_text              : str,
        width                : Union[int, float],
        height               : Union[int, float],
        font                 : str = "msyh.ttc",
        fontsize             : int = 55,
        angle                : Union[int, float] = 45,
        text_stroke_color_rgb: Tuple[int, int, int] = (0, 1, 0),
        text_fill_color_rgb  : Tuple[int, int, int] = (1, 0, 0),
        text_fill_alpha      : Union[int, float] = 0.3,
        num_lines            : Union[int, float] = 1,
        line_spacing         : Union[int, float] = 2,
        word_spacing         : Union[int, float] = 2,
        x_offset             : Union[int, float] = 0,
        y_offset             : Union[int, float] = 0,
        multiple_mode        : bool = False,
        output_path          : str = None,
    ) -> None:
    try:
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
        dump_json(cmd_output_path, {"status": "success", "message": ""})
    except:
        logger.error(traceback.format_exc())
        dump_json(cmd_output_path, {"status": "error", "message": traceback.format_exc()})

def create_image_wartmark(
        width        : Union[int, float],
        height       : Union[int, float],
        wm_image_path: str,
        angle        : Union[int, float] = 0,
        scale        : Union[int, float] = 1,
        opacity      : Union[int, float] = 1,
        num_lines    : Union[int, float] = 1,
        word_spacing : Union[int, float] = 0.1,
        line_spacing : Union[int, float] = 2,
        x_offset     : Union[int, float] = 0,
        y_offset     : Union[int, float] = 0,
        multiple_mode: bool = False,
        output_path  : str = None,
    ):
    try:
        if output_path is None:
            output_path = "watermark.pdf"
        c = canvas.Canvas(output_path,pagesize=(width, height))
        diagonal_length = math.sqrt(width**2 + height**2) # diagonal length of the paper
        wm_image = Image.open(wm_image_path)
        wm_width, wm_height = wm_image.size[0]*scale, wm_image.size[1]*scale
        gap = word_spacing*wm_width
        c.translate(width/2, height/2)
        c.setFillAlpha(opacity)
        c.rotate(angle)
        if multiple_mode:
            start_y_list = list(map(lambda x: x*wm_height*(line_spacing+1), range(num_lines)))
            center_y = sum(start_y_list) / len(start_y_list)
            start_y_list = list(map(lambda x: x - center_y + y_offset, start_y_list))
            logger.debug(start_y_list)
            for start_y in start_y_list:
                start_x = -diagonal_length + x_offset
                while start_x < diagonal_length:
                    c.drawImage(wm_image_path, start_x, start_y, width=wm_width, height=wm_height)
                    start_x += wm_width + gap
        else:
            start_x = -wm_width/2 + x_offset
            start_y = -wm_height/2 + y_offset
            c.drawImage(wm_image_path, start_x, start_y, width=wm_width, height=wm_height)
        c.showPage()
        c.save()
        dump_json(cmd_output_path, {"status": "success", "message": ""})
    except:
        logger.error(traceback.format_exc())
        dump_json(cmd_output_path, {"status": "error", "message": traceback.format_exc()})

@batch_process
def watermark_pdf_by_text(doc_path: str, wm_text: str, page_range: str = "all", output_path: str = None, **args):
    try:
        doc: fitz.Document = fitz.open(doc_path)
        page = doc[-1]
        p = Path(doc_path)
        tmp_wm_path = str(p.parent / "tmp_wm.pdf")
        create_text_wartmark(wm_text=wm_text, width=page.rect.width, height=page.rect.height, output_path=tmp_wm_path, **args)
        wm_doc: fitz.Document = fitz.open(tmp_wm_path)
        roi_indices = parse_range(page_range, doc.page_count)
        for page_index in range(doc.page_count):
            if page_index in roi_indices:
                page: fitz.Page = doc[page_index]
                page.show_pdf_page(page.rect, wm_doc, 0, overlay=False)
                page.clean_contents()
        if output_path is None:
            output_path = p.parent / f"{p.stem}-加水印版.pdf"
        doc.save(output_path, garbage=3, deflate=True)
        wm_doc.close()
        doc.close()
        os.remove(tmp_wm_path)
        dump_json(cmd_output_path, {"status": "success", "message": ""})
    except:
        logger.error(traceback.format_exc())
        dump_json(cmd_output_path, {"status": "error", "message": traceback.format_exc()})

@batch_process
def watermark_pdf_by_image(doc_path: str, wm_path: str, page_range: str = "all", output_path: str = None, **args):
    try:
        doc: fitz.Document = fitz.open(doc_path)
        page = doc[-1]
        p = Path(doc_path)
        tmp_wm_path = str(p.parent / "tmp_wm.pdf")
        create_image_wartmark(wm_image_path=wm_path, width=page.rect.width, height=page.rect.height, output_path=tmp_wm_path, **args)
        wm_doc = fitz.open(tmp_wm_path)
        roi_indices = parse_range(page_range, doc.page_count)
        for i in roi_indices:
            page: fitz.Page = doc[i]
            page.show_pdf_page(page.rect, wm_doc, 0, overlay=False)
            page.clean_contents()
        if output_path is None:
            output_path = p.parent / f"{p.stem}-加水印版.pdf"
        doc.save(output_path, garbage=3, deflate=True)
        wm_doc.close()
        doc.close()
        os.remove(tmp_wm_path)
        dump_json(cmd_output_path, {"status": "success", "message": ""})
    except:
        logger.error(traceback.format_exc())
        dump_json(cmd_output_path, {"status": "error", "message": traceback.format_exc()})

@batch_process
def watermark_pdf_by_pdf(doc_path: str, wm_doc_path: str, page_range: str = "all", output_path: str = None):
    try:
        doc: fitz.Document = fitz.open(doc_path)
        wm_doc: fitz.Document = fitz.open(wm_doc_path)
        roi_indices = parse_range(page_range, doc.page_count)
        for i in roi_indices:
            page: fitz.Page = doc[i]
            page.show_pdf_page(page.rect, wm_doc, 0, overlay=False)
        if output_path is None:
            p = Path(doc_path)
            output_path = p.parent / f"{p.stem}-加水印版.pdf"
        doc.save(output_path, garbage=3, deflate=True)
        wm_doc.close()
        doc.close()
        dump_json(cmd_output_path, {"status": "success", "message": ""})
    except:
        logger.error(traceback.format_exc())
        dump_json(cmd_output_path, {"status": "error", "message": traceback.format_exc()})

@batch_process
def remove_watermark_by_type(doc_path: str, page_range: str = "all", output_path: str = None):
    try:
        doc: fitz.Document = fitz.open(doc_path)
        writer: fitz.Document = fitz.open()
        roi_indices = parse_range(page_range, doc.page_count)
        WATERMARK_FLAG = False
        for page_index in range(doc.page_count):
            page: fitz.Page = doc[page_index]
            if page_index in roi_indices:
                page.clean_contents()
                xref = page.get_contents()[0]
                stream = doc.xref_stream(xref)
                if stream:
                    stream = bytearray(stream)
                    if stream.find(b"/Subtype/Watermark"):
                        WATERMARK_FLAG = True
                        while True:
                            i1 = stream.find(b"/Artifact")  # start of definition
                            if i1 < 0: break  # none more left: done
                            i2 = stream.find(b"EMC", i1)  # end of definition
                            stream[i1 : i2+3] = b""  # remove the full definition source "/Artifact ... EMC"
                        doc.update_stream(xref, stream, compress=True)
            writer.insert_pdf(doc, from_page=page_index, to_page=page_index)
        if not WATERMARK_FLAG:
            logger.error("该文件没有找到水印!")
            dump_json(cmd_output_path, {"status": "error", "message": "该文件没有找到水印!"})
            return
        if output_path is None:
            p = Path(doc_path)
            output_path = str(p.parent / f"{p.stem}-去水印版.pdf")
        writer.ez_save(output_path)
        dump_json(cmd_output_path, {"status": "success", "message": ""})
    except:
        logger.error(traceback.format_exc())
        dump_json(cmd_output_path, {"status": "error", "message": traceback.format_exc()})

@batch_process
def detect_watermark_index_helper(doc_path: str, wm_page_number: int, outpath: str = None):
    try:
        doc: fitz.Document = fitz.open(doc_path)
        writer: fitz.Document = fitz.open()
        page = doc[wm_page_number]
        keys = doc.xref_get_keys(page.xref)
        logger.debug(keys)
        out = doc.xref_get_key(page.xref, "Contents")
        logger.debug(f"Contents: {out}")
        if out[0] == 'array':
            parts = list(out)[1][1:-1].split(" ")
            indirect_objs = list(map(lambda x: " ".join(x), [parts[i:i+3] for i in range(0, len(parts), 3)]))
            for i in range(len(indirect_objs)):
                t = f'[{" ".join(indirect_objs[:i]+indirect_objs[i+1:])}]'
                doc.xref_set_key(page.xref, "Contents", t)
                writer.insert_pdf(doc, from_page=wm_page_number, to_page=wm_page_number)
        if outpath is None:
            p = Path(doc_path)
            outpath = str(p.parent / f"{p.stem}-识别水印索引.pdf")
        if writer.page_count > 0:
            writer.save(outpath, garbage=3, deflate=True)
        else:
            logger.error("该文件没有找到水印!")
            dump_json(cmd_output_path, {"status": "error", "message": "该文件没有找到水印!"})
            return
        dump_json(cmd_output_path, {"status": "success", "message": ""})
    except:
        logger.error(traceback.format_exc())
        dump_json(cmd_output_path, {"status": "error", "message": traceback.format_exc()})
    
@batch_process
def remove_watermark_by_index(doc_path: str, wm_index: List[int], page_range: str = "all", output_path: str = None):
    try:
        doc: fitz.Document = fitz.open(doc_path)
        writer: fitz.Document = fitz.open()
        roi_indices = parse_range(page_range, doc.page_count)
        for i in range(len(wm_index)):
            if wm_index[i] < 0:
                wm_index[i] = doc.page_count + wm_index[i]
        wm_index.sort(reverse=True)
        for page_index in range(doc.page_count):
            page = doc[page_index]
            if page_index in roi_indices:
                out = doc.xref_get_key(page.xref, "Contents")
                if out[0] == 'array':
                    parts = list(out)[1][1:-1].split(" ")
                    indirect_objs = list(map(lambda x: " ".join(x), [parts[i:i+3] for i in range(0, len(parts), 3)]))
                    for i in wm_index:
                        del indirect_objs[i]                    
                    filtered_objs = f'[{" ".join(indirect_objs)}]'
                    doc.xref_set_key(page.xref, "Contents", filtered_objs)
            writer.insert_pdf(doc, from_page=page_index, to_page=page_index)
        if output_path is None:
            p = Path(doc_path)
            output_path = str(p.parent / f"{p.stem}-去水印版.pdf")
        writer.save(output_path, garbage=3, deflate=True)
        dump_json(cmd_output_path, {"status": "success", "message": ""})
    except:
        logger.error(traceback.format_exc())
        dump_json(cmd_output_path, {"status": "error", "message": traceback.format_exc()})

# def insert_header_and_footer(
#         doc_path   : str,
#         content    : str,
#         is_header  : bool = False,
#         margin_bbox: List[float] = [1.27, 1.27, 2.54, 2.54],      # [top, bottom, left, right]
#         font_family: str = "msyh.ttc",
#         font_size  : float = 11,
#         font_color : str = "#000000",
#         opacity    : str = 1,
#         align      : str = "center",
#         page_range : str = "all",
#         unit       : str = "cm",
#         output_path: str = None
#     ):
#     try:
#         doc: fitz.Document = fitz.open(doc_path)
#         roi_indices = parse_range(page_range, doc.page_count)
#         fontpath = str(Path(os.environ['WINDIR']) / "fonts" / font_family)
#         align = {"left": fitz.TEXT_ALIGN_LEFT, "center": fitz.TEXT_ALIGN_CENTER, "right": fitz.TEXT_ALIGN_RIGHT}[align]
#         margin_bbox = [convert_length(x, unit, "pt") for x in margin_bbox]
#         logger.debug(margin_bbox)
#         font_color = [v/255. for v in hex_to_rgb(font_color)]
#         logger.debug(font_color)
#         if is_header:
#             bbox = [margin_bbox[2], 0, doc[-1].rect.width-margin_bbox[3], margin_bbox[0]]
#         else:
#             bbox = [margin_bbox[2], doc[-1].rect.height-margin_bbox[1], doc[-1].rect.width-margin_bbox[3], doc[-1].rect.height]
#         logger.debug(bbox)
#         for page_index in range(doc.page_count):
#             page = doc[page_index]
#             if page_index in roi_indices:
#                 page.insert_textbox(bbox, content, fontsize=font_size, fontname=font_family, fontfile=fontpath, color=font_color, fill_opacity=opacity, align=align, rotate=0)
#         if output_path is None:
#             p = Path(doc_path)
#             output_path = str(p.parent / f"{p.stem}-加页眉页脚.pdf")
#         doc.save(output_path, garbage=3, deflate=True)
#     except:
#         raise ValueError(traceback.format_exc())

def create_header_and_footer_mask(
        width       : float,
        height      : float,
        content_list: List[str],
        margin_bbox : List[float] = [1.27, 1.27, 2.54, 2.54], # [top, bottom, left, right]
        font_family : str = "msyh.ttc",
        font_size   : float = 11,
        font_color  : str = "#000000",
        opacity     : str = 1,
        unit        : str = "cm",
        output_path : str = None
):
    try:
        if output_path is None:
            output_path = "tmp_hf.pdf"
        c = canvas.Canvas(output_path,pagesize=(width, height))
        fontpath = str(Path(os.environ['WINDIR']) / "fonts" / font_family)
        pdfmetrics.registerFont(TTFont('custom_font', fontpath))
        font_color = [v/255. for v in hex_to_rgb(font_color)]
        margin_bbox = [convert_length(x, unit, "pt") for x in margin_bbox]
        c.setFont("custom_font", font_size)
        c.setStrokeColorRGB(*font_color)
        c.setFillColorRGB(*font_color)
        c.setFillAlpha(opacity)
        c.setLineWidth(width-margin_bbox[3]-margin_bbox[2])
        for i, content in enumerate(content_list):
            if content.strip() == "":
                continue
            parts = content.split("\n")
            string_height = c.stringWidth(parts[0][0], "custom_font", font_size)
            if i < 3: # 页眉
                parts = parts[::-1]
                if i == 0:
                    for j, part in enumerate(parts):
                        c.drawString(margin_bbox[2], height-margin_bbox[0]+j*string_height, part)
                elif i == 1:
                    for j, part in enumerate(parts):
                        c.drawCentredString(width/2, height-margin_bbox[0]+j*string_height, part)
                elif i == 2:
                    for j, part in enumerate(parts):
                        c.drawRightString(width-margin_bbox[3], height-margin_bbox[0]+j*string_height, part)
            else: # 页脚
                if i == 3:
                    for j, part in enumerate(parts, 1):
                        c.drawString(margin_bbox[2], margin_bbox[1]-j*string_height, part)
                elif i == 4:
                    for j, part in enumerate(parts, 1):
                        c.drawCentredString(width/2, margin_bbox[1]-j*string_height, part)
                elif i == 5:
                    for j, part in enumerate(parts, 1):
                        c.drawRightString(width-margin_bbox[3], margin_bbox[1]-j*string_height, part)
        c.showPage()
        c.save()
        dump_json(cmd_output_path, {"status": "success", "message": ""})
    except:
        logger.error(traceback.format_exc())
        dump_json(cmd_output_path, {"status": "error", "message": traceback.format_exc()})

@batch_process
def insert_header_and_footer(
        doc_path   : str,
        content_list    : List[str],
        margin_bbox: List[float] = [1.27, 1.27, 2.54, 2.54],      # [top, bottom, left, right]
        font_family: str = "msyh.ttc",
        font_size  : float = 11,
        font_color : str = "#000000",
        opacity    : str = 1,
        page_range : str = "all",
        unit       : str = "cm",
        output_path: str = None
    ):
    try:
        doc: fitz.Document = fitz.open(doc_path)
        width, height = doc[-1].rect.width, doc[-1].rect.height
        p = Path(doc_path)
        # 生成页眉页脚pdf(相比page.insert_text,此方法生成体积更小)
        hf_output_path = str(p.parent / "tmp_hf.pdf")
        create_header_and_footer_mask(width=width, height=height, content_list=content_list, margin_bbox=margin_bbox,font_family=font_family, font_size=font_size, font_color=font_color, opacity=opacity, unit=unit, output_path=hf_output_path)
        # 插入页眉页脚
        hf_doc = fitz.open(hf_output_path)
        roi_indicies = parse_range(page_range, doc.page_count)
        for page_index in range(doc.page_count):
            page = doc[page_index]
            if page_index in roi_indicies:
                page.show_pdf_page(page.rect, hf_doc, 0, overlay=False)
                page.clean_contents()
        if output_path is None:
            output_path = str(p.parent / f"{p.stem}-加页眉页脚.pdf")
        doc.save(output_path, garbage=3, deflate=True)
        doc.close()
        hf_doc.close()
        os.remove(hf_output_path)
        dump_json(cmd_output_path, {"status": "success", "message": ""})
    except:
        logger.error(traceback.format_exc())
        dump_json(cmd_output_path, {"status": "error", "message": traceback.format_exc()})

@batch_process
def insert_page_number(
        doc_path   : str,
        format     : str,
        pos        : str        = "footer",
        start      : int         = 0,
        margin_bbox: List[float] = [1.27, 1.27, 2.54, 2.54],
        font_family: str         = "msyh.ttc",
        font_size  : float      = 11,
        font_color : str        = "#000000",
        opacity    : str        = 1,
        align      : str        = "center",
        page_range : str        = "all",
        unit       : str        = "cm",
        output_path: str         = None
    ):
    """ 页码样式
    {
        "0":"1,2,3...",
        "1":"1/X",
        "2":"第1页",
        "3":"第1/X页",
        "4":"第1页，共X页",
        "5":"-1-,-2-,-3-...",
        "6":"第一页",
        "7":"第一页，共X页",
        "8":"I,II,III...",
        "9":"i,ii,iii...",
        "10":"A,B,C...",
        "11":"a,b,c...",
    }
    """
    try:
        doc: fitz.Document = fitz.open(doc_path)
        roi_indices = parse_range(page_range, doc.page_count)
        pno = start
        for page_index in range(doc.page_count):
            page = doc[page_index]
            if page_index in roi_indices:
                if format == "0":
                    content = f"{pno}"
                elif format == "1":
                    content = f"{pno}/{doc.page_count}"
                elif format == "2":
                    content = f"第{pno}页"
                elif format == "3":
                    content = f"第{pno}/{doc.page_count}页"
                elif format == "4":
                    content = f"第{pno}页，共{doc.page_count}页"
                elif format == "5":
                    content = f"-{pno}-"
                elif format == "6":
                    content = f"第{num_to_chinese(pno)}页"
                elif format == "7":
                    content = f"第{num_to_chinese(pno)}页，共{num_to_chinese(doc.page_count)}页"
                elif format == "8":
                    content = f"{num_to_roman(pno)}"
                elif format == "9":
                    content = f"{num_to_roman(pno).lower()}"
                elif format == "10":
                    content = f"{num_to_letter(pno)}"
                elif format == "11":
                    content = f"{num_to_letter(pno).lower()}"
                else:
                    content = format.replace("%p", str(pno)).replace("%P", str(doc.page_count))
                pno += 1
                hf_output_path = str(Path(doc_path).parent / f"tmp_hf.pdf")
                content_list = [""]*6
                if pos == "header":
                    if align == "left":
                        content_list[0] = content
                    elif align == "center":
                        content_list[1] = content
                    elif align == "right":
                        content_list[2] = content
                else:
                    if align == "left":
                        content_list[3] = content
                    elif align == "center":
                        content_list[4] = content
                    elif align == "right":
                        content_list[5] = content
                create_header_and_footer_mask(width=page.rect.width, height=page.rect.height, content_list=content_list, margin_bbox=margin_bbox,font_family=font_family, font_size=font_size, font_color=font_color, opacity=opacity, unit=unit, output_path=hf_output_path)
                hf_doc: fitz.Document = fitz.open(hf_output_path)
                page.show_pdf_page(page.rect, hf_doc, 0, overlay=True)
        if output_path is None:
            p = Path(doc_path)
            output_path = str(p.parent / f"{p.stem}-加页码.pdf")
        doc.save(output_path, garbage=3, deflate=True)
        hf_doc.close()
        doc.close()
        os.remove(hf_output_path)
        dump_json(cmd_output_path, {"status": "success", "message": ""})
    except:
        logger.error(traceback.format_exc())
        dump_json(cmd_output_path, {"status": "error", "message": traceback.format_exc()})

@batch_process
def remove_header_and_footer(doc_path: str,  margin_bbox: List[float], remove_list: List[str] = ['header', 'footer'], unit: str = "cm", page_range: str = "all", output_path: str = None):
    try:
        doc: fitz.Document = fitz.open(doc_path)
        width, height = doc[-1].rect.width, doc[-1].rect.height
        roi_indices = parse_range(page_range, doc.page_count)
        margin_bbox = [convert_length(x, unit, "pt") for x in margin_bbox]
        p = Path(doc_path)
        mask_doc_path = str(p.parent / "tmp_mask.pdf")
        c = canvas.Canvas(mask_doc_path,pagesize=(width, height))
        color = [v/255. for v in hex_to_rgb("#FFFFFF")]
        bbox_list = []
        if "header" in remove_list:
            bbox_list.append([margin_bbox[2], height-margin_bbox[0], width-margin_bbox[2]-margin_bbox[3], margin_bbox[0]]) # left_bottom_x, left_bottom_y, w, h
        if "footer" in remove_list:
            bbox_list.append([margin_bbox[2], 0, width-margin_bbox[2]-margin_bbox[3], margin_bbox[1]])
        for bbox in bbox_list:
            c.setStrokeColorRGB(*color)
            c.setFillColorRGB(*color)
            c.rect(*bbox, fill=True, stroke=False)
        c.showPage()
        c.save()
        mask_doc = fitz.open(mask_doc_path)
        for page_index in range(doc.page_count):
            if page_index in roi_indices:
                page = doc[page_index]
                page.show_pdf_page(page.rect, mask_doc, 0, overlay=True)
                page.clean_contents()
        if output_path is None:
            output_path = str(p.parent / f"{p.stem}-去页眉页脚.pdf")
        doc.save(output_path, garbage=3, deflate=True)
        doc.close()
        mask_doc.close()
        os.remove(mask_doc_path)
        dump_json(cmd_output_path, {"status": "success", "message": ""})
    except:
        logger.error(traceback.format_exc())
        dump_json(cmd_output_path, {"status": "error", "message": traceback.format_exc()})

@batch_process
def remove_page_number(doc_path: str, margin_bbox: List[float], pos: str = "footer", unit: str = "cm", page_range: str = "all", output_path: str = None):
    try:
        remove_header_and_footer(doc_path=doc_path, margin_bbox=margin_bbox, remove_list=[pos], unit=unit, page_range=page_range, output_path=output_path)
        dump_json(cmd_output_path, {"status": "success", "message": ""})
    except:
        logger.error(traceback.format_exc())
        dump_json(cmd_output_path, {"status": "error", "message": traceback.format_exc()})

@batch_process
def add_doc_background_by_color(
        doc_path   : str,
        color      : str = "#FFFFFF",
        opacity    : float = 1,
        angle      : float = 0,
        x_offset   : float = 0,
        y_offset   : float = 0,
        page_range : str = "all",
        output_path: str = None
    ):
    try:
        doc: fitz.Document = fitz.open(doc_path)
        color = [v/255. for v in hex_to_rgb(color)]
        width = doc[-1].rect.width
        height = doc[-1].rect.height
        logger.debug(doc[-1].rect)
        p = Path(doc_path)
        bg_output_path = str(p.parent / "tmp_bg.pdf")
        c = canvas.Canvas(bg_output_path, pagesize=(width, height))
        c.setStrokeColorRGB(*color)
        c.setFillColorRGB(*color)
        c.setFillAlpha(opacity)
        c.translate(width/2, height/2)
        c.rotate(angle)
        c.rect(-width/2+x_offset, -height/2+y_offset, width, height, fill=True, stroke=False)
        c.showPage()
        c.save()
        
        bg_doc = fitz.open(bg_output_path)
        roi_indicies = parse_range(page_range, doc.page_count)
        for page_index in range(doc.page_count):
            page = doc[page_index]
            if page_index in roi_indicies:
                page.show_pdf_page(page.rect, bg_doc, 0, overlay=False)
                page.clean_contents()
        if output_path is None:
            output_path = str(p.parent / f"{p.stem}-加背景.pdf")
        doc.save(output_path, garbage=3, deflate=True)
        doc.close()
        bg_doc.close()
        os.remove(bg_output_path)
        dump_json(cmd_output_path, {"status": "success", "message": ""})
    except:
        logger.error(traceback.format_exc())
        dump_json(cmd_output_path, {"status": "error", "message": traceback.format_exc()})

@batch_process
def add_doc_background_by_image(
        doc_path   : str,
        img_path   : str,
        opacity    : float = 1,
        angle      : float = 0,
        x_offset   : float = 0,
        y_offset   : float = 0,
        scale      : float = 1,
        page_range : str = "all",
        output_path: str = None
    ):
    try:
        doc: fitz.Document = fitz.open(doc_path)
        width = doc[-1].rect.width
        height = doc[-1].rect.height
        logger.debug(doc[-1].rect)
        p = Path(doc_path)
        bg_output_path = str(p.parent / "tmp_bg.pdf")
        
        c = canvas.Canvas(bg_output_path, pagesize=(width, height))
        c.setFillAlpha(opacity)
        c.translate(width/2, height/2)
        c.rotate(angle)
        img = Image.open(img_path)
        img_width, img_height = img.size
        scaled_w, scaled_h = img_width*scale, img_height*scale
        c.drawImage(img_path, -scaled_w/2+x_offset, -scaled_h/2+y_offset, width=scaled_w, height=scaled_h)
        c.showPage()
        c.save()

        bg_doc = fitz.open(bg_output_path)
        roi_indicies = parse_range(page_range, doc.page_count)
        for page_index in range(doc.page_count):
            page = doc[page_index]
            if page_index in roi_indicies:
                page.show_pdf_page(page.rect, bg_doc, 0, overlay=False)
                page.clean_contents()
        if output_path is None:
            output_path = str(p.parent / f"{p.stem}-加背景.pdf")
        doc.save(output_path, garbage=3, deflate=True)
        doc.close()
        bg_doc.close()
        os.remove(bg_output_path)
        dump_json(cmd_output_path, {"status": "success", "message": ""})
    except:
        logger.error(traceback.format_exc())
        dump_json(cmd_output_path, {"status": "error", "message": traceback.format_exc()})

@batch_process
def mask_pdf_by_rectangle(
        doc_path   : str,
        bbox_list  : List[List[float]],
        color      : str = "#FFFFFF",
        opacity    : float = 1,
        angle      : float = 0,
        overlay    : bool = True,
        page_range : str = "all",
        unit       : str = "pt",
        output_path: str = None
    ):
    try:
        doc: fitz.Document = fitz.open(doc_path)
        width, height = doc[-1].rect.width, doc[-1].rect.height
        p = Path(doc_path)
        mask_doc_path = str(p.parent / "tmp_mask.pdf")
        c = canvas.Canvas(mask_doc_path,pagesize=(width, height))
        color = [v/255. for v in hex_to_rgb(color)]
        logger.debug(bbox_list)
        logger.debug(doc[-1].rect)
        for bbox in bbox_list:
            bbox = [convert_length(x, unit, "pt") for x in bbox]
            bbox[1], bbox[3] = height-bbox[1], height-bbox[3]
            c.setStrokeColorRGB(*color)
            c.setFillColorRGB(*color)
            c.setFillAlpha(opacity)
            c.rotate(angle)
            box_w, box_h = bbox[2]-bbox[0], bbox[3]-bbox[1]
            c.rect(bbox[0], bbox[1], box_w, box_h, fill=True, stroke=False)
        c.showPage()
        c.save()

        mask_doc: fitz.Document = fitz.open(mask_doc_path)
        roi_indicies = parse_range(page_range, doc.page_count)
        for page_index in range(doc.page_count):
            page = doc[page_index]
            if page_index in roi_indicies:
                page.show_pdf_page(page.rect, mask_doc, 0, overlay=overlay)
                page.clean_contents()
        if output_path is None:
            output_path = str(p.parent / f"{p.stem}-加遮罩.pdf")
        doc.save(output_path, garbage=3, deflate=True)
        doc.close()
        mask_doc.close()
        os.remove(mask_doc_path)
        dump_json(cmd_output_path, {"status": "success", "message": ""})
    except:
        logger.error(traceback.format_exc())
        dump_json(cmd_output_path, {"status": "error", "message": traceback.format_exc()})

@batch_process
def mask_pdf_by_rectangle_annot(
        doc_path   : str,
        annot_page : int = 0,
        color      : str = "#FFFFFF",
        opacity    : float = 1,
        angle      : float = 0,
        page_range : str = "all",
        output_path: str = None
    ):
    try:
        doc: fitz.Document = fitz.open(doc_path)
        page = doc[annot_page]
        rect_list = []
        for annot in page.annots():
            if annot.type[0] == 4: # Square
                rect_list.append(annot.rect)
            page.delete_annot(annot)
        logger.debug(rect_list)
        if rect_list:
            p = Path(doc_path)
            clean_doc_path = str(p.parent / "tmp_clean.pdf")
            doc.save(clean_doc_path, garbage=3, deflate=True)
            if output_path is None:
                output_path = str(p.parent / f"{p.stem}-批注遮罩版.pdf")
            mask_pdf_by_rectangle(doc_path=clean_doc_path, bbox_list=rect_list, color=color, opacity=opacity, angle=angle, page_range=page_range, output_path=output_path)
            os.remove(clean_doc_path)
        else:
            logger.error("没有找到矩形注释!")
            dump_json(cmd_output_path, {"status": "error", "message": "没有找到矩形注释!"})
            return
        dump_json(cmd_output_path, {"status": "success", "message": ""})
    except:
        logger.error(traceback.format_exc())
        dump_json(cmd_output_path, {"status": "error", "message": traceback.format_exc()})


def convert_to_image_pdf(doc_path: str, dpi: int = 300, page_range: str = "all", output_path: str = None):
    try:
        doc: fitz.Document = fitz.open(doc_path)
        writer: fitz.Document = fitz.open()
        roi_indices = parse_range(page_range, doc.page_count)
        toc = doc.get_toc(simple=True)
        logger.debug(toc)
        for page_index in range(doc.page_count):
            page = doc[page_index]
            new_page = writer.new_page(width=page.rect.width, height=page.rect.height)
            if page_index in roi_indices:
                pix = page.get_pixmap(matrix=fitz.Matrix(dpi/72, dpi/72))
                pix.set_dpi(dpi, dpi)
                new_page.insert_image(new_page.rect, pixmap=pix)
            else:
                writer.insert_pdf(doc, from_page=page_index, to_page=page_index)
        if output_path is None:
            p = Path(doc_path)
            output_path = str(p.parent / f"{p.stem}-图片型.pdf")
        writer.set_toc(toc)
        writer.ez_save(output_path)
        dump_json(cmd_output_path, {"status": "success", "message": ""})
    except:
        logger.error(traceback.format_exc())
        dump_json(cmd_output_path, {"status": "error", "message": traceback.format_exc()})

def convert_pdf2png(doc_path: str, dpi: int = 300, page_range: str = "all", output_path: str = None):
    try:
        doc: fitz.Document = fitz.open(doc_path)
        roi_indices = parse_range(page_range, doc.page_count)
        if output_path is None:
            p = Path(doc_path)
            output_dir = p.parent / f"{p.stem}-png"
            output_dir.mkdir(exist_ok=True, parents=True)
        else:
            output_dir = Path(output_path)
            output_dir.mkdir(exist_ok=True, parents=True)
        for i in roi_indices:
            page = doc[i]
            pix = page.get_pixmap(matrix=fitz.Matrix(dpi/72, dpi/72))
            pix.set_dpi(dpi, dpi)
            pix.save(str(output_dir / f"page-{i+1}.png"))
        dump_json(cmd_output_path, {"status": "success", "message": ""})
    except:
        logger.error(traceback.format_exc())
        dump_json(cmd_output_path, {"status": "error", "message": traceback.format_exc()})

def convert_pdf2svg(doc_path: str, dpi: int = 300, page_range: str = "all", output_path: str = None):
    try:
        doc: fitz.Document = fitz.open(doc_path)
        roi_indices = parse_range(page_range, doc.page_count)
        if output_path is None:
            p = Path(doc_path)
            output_dir = p.parent / f"{p.stem}-svg"
            output_dir.mkdir(exist_ok=True, parents=True)
        else:
            output_dir = Path(output_path)
            output_dir.mkdir(exist_ok=True, parents=True)
        for i in roi_indices:
            page = doc[i]
            out = page.get_svg_image(matrix=fitz.Matrix(dpi/72, dpi/72))
            with open(str(output_dir / f"page-{i+1}.svg"), "w") as f:
                f.write(out)
        dump_json(cmd_output_path, {"status": "success", "message": ""})
    except:
        logger.error(traceback.format_exc())
        dump_json(cmd_output_path, {"status": "error", "message": traceback.format_exc()})

def convert_svg2pdf(input_path: Union[str, List[str]], is_merge: bool = True, output_path: str = None):
    try:
        if isinstance(input_path, str):
            path_list = [input_path]
        else:
            path_list = input_path
        if is_merge:
            writer: fitz.Document = fitz.open()
            for path in path_list:
                with open(path, 'r') as f:
                    img = fitz.open(path)
                    pdfbytes = img.convert_to_pdf()
                    pdf = fitz.open('pdf', pdfbytes)
                    rect = img[0].rect
                    page = writer.new_page(width=rect.width, height=rect.height)
                    page.show_pdf_page(rect, pdf, 0)
            if output_path is None:
                p = Path(path_list[0])
                output_path = str(p.parent / f"{p.stem}(等)-合并.pdf")
            writer.save(output_path, garbage=3, deflate=True)
        else:
            if output_path is None:
                p = Path(path_list[0])
                output_dir = p.parent / f"{p.stem}(等)-pdf"
                output_dir.mkdir(exist_ok=True, parents=True)
            else:
                output_dir = Path(output_path)
                output_dir.mkdir(exist_ok=True, parents=True)
            for path in path_list:
                with open(path, 'r') as f:
                    img = fitz.open(path)
                    pdfbytes = img.convert_to_pdf()
                    pdf = fitz.open('pdf', pdfbytes) 
                    pdf.save(str(output_dir / f"{Path(path).stem}.pdf"), garbage=3, deflate=True)
        dump_json(cmd_output_path, {"status": "success", "message": ""})
    except:
        logger.error(traceback.format_exc())
        dump_json(cmd_output_path, {"status": "error", "message": traceback.format_exc()})

def convert_png2pdf(input_path: Union[str, List[str]], is_merge: bool = True, output_path: str = None):
    convert_svg2pdf(input_path, is_merge, output_path)

def convert_anydoc2pdf(input_path: str, output_path: str = None):
    """
    supported document types: PDF, XPS, EPUB, MOBI, FB2, CBZ, SVG
    """
    try:
        doc = fitz.open(input_path)
        b = doc.convert_to_pdf()  # convert to pdf
        pdf = fitz.open("pdf", b)  # open as pdf

        toc= doc.get_toc()  # table of contents of input
        pdf.set_toc(toc)  # simply set it for output
        meta = doc.metadata  # read and set metadata
        if not meta["producer"]:
            meta["producer"] = "PyMuPDF v" + fitz.VersionBind

        if not meta["creator"]:
            meta["creator"] = "PyMuPDF PDF converter"
        meta["modDate"] = fitz.get_pdf_now()
        meta["creationDate"] = meta["modDate"]
        pdf.set_metadata(meta)

        # now process the links
        link_cnti = 0
        link_skip = 0
        for pinput in doc:  # iterate through input pages
            links = pinput.get_links()  # get list of links
            link_cnti += len(links)  # count how many
            pout = pdf[pinput.number]  # read corresp. output page
            for l in links:  # iterate though the links
                if l["kind"] == fitz.LINK_NAMED:  # we do not handle named links
                    logger.info("named link page", pinput.number, l)
                    link_skip += 1  # count them
                    continue
                pout.insert_link(l)  # simply output the others

        # save the conversion result
        if output_path is None:
            p = Path(input_path)
            output_path = str(p.parent / f"{p.stem}.pdf")
        pdf.save(output_path, garbage=4, deflate=True)
        dump_json(cmd_output_path, {"status": "success", "message": ""})
    except:
        logger.error(traceback.format_exc())
        dump_json(cmd_output_path, {"status": "error", "message": traceback.format_exc()})

def extract_metadata(doc_path: str, output_path: str = None):
    try:
        doc: fitz.Document = fitz.open(doc_path)
        out = doc.metadata
        logger.debug(out)
        # embfile_info = doc.embfile_info()
        # logger.debug(embfile_info)

        out = doc.chapter_count
        logger.debug(out)

        catalog = doc.pdf_catalog()
        logger.debug(catalog)

        perm = doc.permissions
        logger.debug(perm)

        metadata = {}  # make my own metadata dict
        what, value = doc.xref_get_key(-1, "Info")  # /Info key in the trailer
        if what != "xref":
            pass  # PDF has no metadata
        else:
            xref = int(value.replace("0 R", ""))  # extract the metadata xref
            for key in doc.xref_get_keys(xref):
                metadata[key] = doc.xref_get_key(xref, key)[1]
        metadata['page_count'] = doc.page_count
        page_size = doc[-1].rect
        metadata['page_size'] = (convert_length(page_size.width, "pt", "cm"), convert_length(page_size.height, "pt", "cm"))
        file_size = os.path.getsize(doc_path)
        metadata['file_size'] = human_readable_size(file_size)
        logger.debug(metadata)
        dump_json(cmd_output_path, {"status": "success", "message": ""})
    except:
        logger.error(traceback.format_exc())
        dump_json(cmd_output_path, {"status": "error", "message": traceback.format_exc()})

def flags_decomposer(flags):
    """Make font flags human readable."""
    l = []
    if flags & 2 ** 0:
        l.append("superscript")
    if flags & 2 ** 1:
        l.append("italic")
    if flags & 2 ** 2:
        l.append("serifed")
    else:
        l.append("sans")
    if flags & 2 ** 3:
        l.append("monospaced")
    else:
        l.append("proportional")
    if flags & 2 ** 4:
        l.append("bold")
    return ", ".join(l)

def extract_fonts(doc_path: str, output_path: str = None):
    try:
        doc: fitz.Document = fitz.open(doc_path)
        page = doc[0]

        # read page text as a dictionary, suppressing extra spaces in CJK fonts
        out = page.get_text("json")
        with open("out-json.json", "w", encoding="utf-8") as f:
            json.dump(out, f, indent=2, ensure_ascii=False)
        
        wlist = page.get_text("words")
        with open("out-words.json", "w", encoding="utf-8") as f:
            json.dump(wlist, f, indent=2, ensure_ascii=False)
        
        out = page.get_text("dict", flags=11)
        with open("out-dict.json", "w", encoding="utf-8") as f:
            json.dump(out, f, indent=2, ensure_ascii=False)

        blocks = page.get_text("dict", flags=11)["blocks"]
        with open("out-blocks.json", "w", encoding="utf-8") as f:
            json.dump(blocks, f, indent=2, ensure_ascii=False)
        logger.debug(blocks)
        for b in blocks:  # iterate through the text blocks
            for l in b["lines"]:  # iterate through the text lines
                for s in l["spans"]:  # iterate through the text spans
                    # logger.debug("")
                    font_properties = "Font: '%s' (%s), size %g, color #%06x" % (
                        s["font"],  # font name
                        flags_decomposer(s["flags"]),  # readable font flags
                        s["size"],  # font size
                        s["color"],  # font color
                    )
                    # logger.debug("Text: '%s'" % s["text"])  # simple print of text
                    # logger.debug(font_properties)
    except:
        logger.error(traceback.format_exc())
        dump_json(cmd_output_path, {"status": "error", "message": traceback.format_exc()})

def make_dual_layer_pdf(input_path: str, page_range: str = 'all', lang: str = 'chi_sim', dpi: int = 300, output_path: str = None):
    try:
        tesseract_path = None
        with open("config.json", "r") as f:
            config = json.load(f)
            if not config['tesseract_path']:
                dump_json(cmd_output_path, {"status": "error", "message": "请先配置tesseract路径"})
                return
            tesseract_path = config['tesseract_path']

        # tesseract_path = "C:\\Program Files\\Tesseract-OCR\\tesseract.exe"
        doc: fitz.Document = fitz.open(input_path)
        writer: fitz.Document = fitz.open()
        roi_indices = parse_range(page_range, doc.page_count)
        toc = doc.get_toc(simple=True)

        p = Path(input_path)
        temp_dir = p.parent / "temp"
        temp_dir.mkdir(exist_ok=True, parents=True)

        for page_index in range(doc.page_count):
            page = doc[page_index]
            if page_index in roi_indices:
                pix = page.get_pixmap(matrix=fitz.Matrix(dpi/72, dpi/72))
                img_save_path = str(temp_dir / f"{page_index}.png")
                pix.pil_save(img_save_path, dpi=(dpi, dpi))
                pdf_save_path = str(temp_dir / f"{page_index}")
                result = subprocess.run([tesseract_path, img_save_path, pdf_save_path, "-l", lang, "pdf"], capture_output=True, text=True, creationflags=subprocess.CREATE_NO_WINDOW)
                if result.returncode != 0:
                    logger.error(result)
                    dump_json(cmd_output_path, {"status": "error", "message": str(result)})
                    return
                else:
                    new_page = writer.new_page(width=page.rect.width, height=page.rect.height)
                    pdf = fitz.open(f"{pdf_save_path}.pdf")
                    new_page.show_pdf_page(page.rect, pdf, 0)
                    pdf.close()
            else:
                writer.insert_pdf(doc, from_page=page_index, to_page=page_index)

        writer.set_toc(toc)
        if output_path is None:
            output_path = p.parent / f"{p.stem}-双层.pdf"
        writer.ez_save(output_path)
        writer.close()
        doc.close()
        shutil.rmtree(temp_dir)
        dump_json(cmd_output_path, {"status": "success", "message": ""})
    except:
        logger.error(traceback.format_exc())
        dump_json(cmd_output_path, {"status": "error", "message": traceback.format_exc()})

@batch_process
def make_dual_layer_pdf_from_image(doc_path: str, lang: str = 'chi_sim',  output_path: str = None):
    try:
        tesseract_path = None
        with open("config.json", "r") as f:
            config = json.load(f)
            if not config['tesseract_path']:
                dump_json(cmd_output_path, {"status": "error", "message": "请先配置tesseract路径"})
                return
            tesseract_path = config['tesseract_path']
        if output_path is None:
            p = Path(doc_path)
            output_path = p.parent / f"{p.stem}-双层"
        result = subprocess.run([tesseract_path, doc_path, output_path, "-l", lang, "pdf"], capture_output=True, text=True, creationflags=subprocess.CREATE_NO_WINDOW)
        if result.returncode != 0:
            logger.error(result)
            dump_json(cmd_output_path, {"status": "error", "message": str(result)})
            return
    except:
        logger.error(traceback.format_exc())
        dump_json(cmd_output_path, {"status": "error", "message": traceback.format_exc()})

def main():
    parser = argparse.ArgumentParser()
    sub_parsers = parser.add_subparsers()
    # 合并子命令
    merge_parser = sub_parsers.add_parser("merge", help="合并", description="合并pdf文件")
    merge_parser.set_defaults(which='merge')
    merge_parser.add_argument("input_path_list", type=str, nargs="+", help="pdf文件路径")
    merge_parser.add_argument("-o", "--output", type=str, help="输出文件路径")
    merge_parser.add_argument("--sort_method", type=str, choices=['default', 'name', 'name_digit', 'ctime', 'mtime'], default="default", help="排序方式")
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
    insert_parser.add_argument("--insert_pos", type=int, default=0, help="插入位置页码")
    insert_parser.add_argument("--pos-type", type=str, choices=['before_first', 'after_first', 'before_last', 'after_last', 'before_custom', 'after_custom'], default="before", help="插入位置类型")
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
    bookmark_transform_parser.add_argument("--add_offset", type=int, default=0, help="页码偏移量")
    bookmark_transform_parser.add_argument("--level-dict", type=str, action="append", help="目录层级字典")
    bookmark_transform_parser.add_argument("--delete-level-below", type=int, default=0, help="删除目录层级")
    bookmark_transform_parser.add_argument("--default-level", type=int, default=1, help="默认目录层级")
    bookmark_transform_parser.add_argument("--remove-blank-lines", action="store_true", help="删除空行")
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
    resize_parser.add_argument("--unit", type=str, choices=['pt', 'mm', 'cm', 'in'], default="pt", help="单位")
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
    convert_parser.add_argument("--source-type", type=str, default="pdf", help="源类型")
    convert_parser.add_argument("--target-type", type=str, default="png", help="目标类型")
    convert_parser.add_argument("--dpi", type=int, default=300, help="分辨率")
    convert_parser.add_argument("--is_merge", action="store_true", help="是否合并")
    convert_parser.add_argument("-o", "--output", type=str, help="输出文件路径")

    # 遮罩子命令
    mask_parser = sub_parsers.add_parser("mask", help="遮罩", description="遮罩pdf文件")
    mask_parser.set_defaults(which='mask')
    mask_parser.add_argument("input_path", type=str, help="pdf文件路径")
    mask_parser.add_argument("--page_range", type=str, default="all", help="页码范围")
    mask_parser.add_argument("--type", type=str, choices=['rect', 'annot'], default="rectangle", help="遮罩类型")
    mask_parser.add_argument("--bbox", type=float, nargs=4, action='append', help="遮罩框")
    mask_parser.add_argument("--color", type=str, default="#FFFFFF", help="遮罩颜色")
    mask_parser.add_argument("--opacity", type=float, default=0.5, help="遮罩不透明度")
    mask_parser.add_argument("--angle", type=float, default=0, help="遮罩旋转角度")
    mask_parser.add_argument("--unit", type=str, choices=['pt', 'mm', 'cm', 'in'], default="pt", help="单位")
    mask_parser.add_argument("--annot-page", type=int, default=0, help="批注所在页码")
    mask_parser.add_argument("-o", "--output", type=str, help="输出文件路径")

    # 背景子命令
    bg_parser = sub_parsers.add_parser("bg", help="背景", description="添加背景")
    bg_parser.set_defaults(which='bg')
    bg_parser.add_argument("input_path", type=str, help="pdf文件路径")
    bg_parser.add_argument("--page_range", type=str, default="all", help="页码范围")
    bg_parser.add_argument("--type", type=str, choices=['color', 'image'], default="color", help="背景类型")
    bg_parser.add_argument("--color", type=str, default="#FFFFFF", help="背景颜色")
    bg_parser.add_argument("--opacity", type=float, default=0.5, help="背景不透明度")
    bg_parser.add_argument("--angle", type=float, default=0, help="背景旋转角度")
    bg_parser.add_argument("--x-offset", type=float, default=0, help="背景x轴偏移量")
    bg_parser.add_argument("--y-offset", type=float, default=0, help="背景y轴偏移量")
    bg_parser.add_argument("--scale", type=float, default=1, help="背景缩放比例")
    bg_parser.add_argument("--img-path", type=str, help="背景图片路径")
    bg_parser.add_argument("-o", "--output", type=str, help="输出文件路径")

    # 页眉页脚子命令
    header_footer_parser = sub_parsers.add_parser("header_footer", help="页眉页脚", description="添加页眉页脚")
    header_footer_parser.set_defaults(which='header_footer')
    header_footer_parser.add_argument("--type", type=str, choices=['add', 'remove'], default="add", help="操作类型")
    header_footer_parser.add_argument("input_path", type=str, help="pdf文件路径")
    header_footer_parser.add_argument("--page-range", type=str, default="all", help="页码范围")
    header_footer_parser.add_argument("--header-left", type=str, help="页眉左侧内容")
    header_footer_parser.add_argument("--header-center", type=str, help="页眉中间内容")
    header_footer_parser.add_argument("--header-right", type=str, help="页眉右侧内容")
    header_footer_parser.add_argument("--footer-left", type=str, help="页脚左侧内容")
    header_footer_parser.add_argument("--footer-center", type=str, help="页脚中间内容")
    header_footer_parser.add_argument("--footer-right", type=str, help="页脚右侧内容")
    header_footer_parser.add_argument("--font-family", type=str, help="字体类型")
    header_footer_parser.add_argument("--font-size", type=int, default=10, help="字体大小")
    header_footer_parser.add_argument("--font-color", type=str, default="#000000", help="字体颜色")
    header_footer_parser.add_argument("--opacity", type=float, default=1, help="字体不透明度")
    header_footer_parser.add_argument("--margin-bbox", type=float, nargs=4, default=[1.27, 1.27, 2.54, 2.54], help="页眉页脚边框, [上,下,左,右]")
    header_footer_parser.add_argument("--unit", type=str, choices=['pt', 'mm', 'cm', 'in'], default="cm", help="单位")
    header_footer_parser.add_argument("--remove", type=str, nargs="+", default=['header', 'footer'], help="删除页眉页脚")
    header_footer_parser.add_argument("-o", "--output", type=str, help="输出文件路径")

    # 页码子命令
    page_number_parser = sub_parsers.add_parser("page_number", help="页码", description="添加页码")
    page_number_parser.set_defaults(which='page_number')
    page_number_parser.add_argument("input_path", type=str, help="pdf文件路径")
    page_number_parser.add_argument("--type", type=str, choices=['add', 'remove'], default="add", help="操作类型")
    page_number_parser.add_argument("--page-range", type=str, default="all", help="页码范围")
    page_number_parser.add_argument("--start", type=int, default=1, help="起始页码")
    page_number_parser.add_argument("--format", type=str, default="第%p页", help="页码格式")
    page_number_parser.add_argument("--pos", type=str, choices=['header', 'footer'], default="footer", help="页码位置")
    page_number_parser.add_argument("--align", type=str, choices=['left', 'center', 'right'], default="right", help="页码对齐方式")
    page_number_parser.add_argument("--font-family", type=str, help="字体类型")
    page_number_parser.add_argument("--font-size", type=int, default=10, help="字体大小")
    page_number_parser.add_argument("--font-color", type=str, default="#000000", help="字体颜色")
    page_number_parser.add_argument("--opacity", type=float, default=1, help="字体不透明度")
    page_number_parser.add_argument("--margin-bbox", type=float, nargs=4, help="页眉页脚边框, [上,下,左,右]")
    page_number_parser.add_argument("--unit", type=str, choices=['pt', 'mm', 'cm', 'in'], default="pt", help="单位")
    page_number_parser.add_argument("-o", "--output", type=str, help="输出文件路径")

    # 双层PDF子命令
    dual_parser = sub_parsers.add_parser("dual", help="双层PDF", description="生成双层PDF")
    dual_parser.set_defaults(which='dual')
    dual_parser.add_argument("input_path", type=str, help="pdf文件路径")
    dual_parser.add_argument("--dpi", type=int, default=300, help="分辨率")
    dual_parser.add_argument("--page-range", type=str, default="all", help="页码范围")
    dual_parser.add_argument("--lang", type=str, default="ch", help="识别语言") # ['chi_sim', 'eng']
    dual_parser.add_argument("-o", "--output", type=str, help="输出文件路径")

    args = parser.parse_args()
    logger.debug(args)
    if args.which == "merge":
        merge_pdf(doc_path_list=args.input_path_list, sort_method=args.sort_method, sort_direction=args.sort_direction, output_path=args.output)
    elif args.which == "split":
        if args.mode == "chunk":
            split_pdf_by_chunk(doc_path=args.input_path, chunk_size=args.chunk_size, output_path=args.output)
        elif args.mode == "page":
            split_pdf_by_page(doc_path=args.input_path, page_range=args.page_range, output_path=args.output)
        elif args.mode == "toc":
            split_pdf_by_toc(doc_path=args.input_path, level=args.toc_level, output_path=args.output)
    elif args.which == "delete":
        slice_pdf(doc_path=args.input_path, page_range=args.page_range, output_path=args.output, is_reverse=True)
    elif args.which == 'insert':
        if args.method == "blank":
            insert_blank_pdf(doc_path=args.input_path1, pos=args.insert_pos, pos_type=args.pos_type, count=args.count, orientation=args.orientation, paper_size=args.paper_size, output_path=args.output)
        else:
            insert_pdf(doc_path1=args.input_path1, doc_path2=args.input_path2, insert_pos=args.insert_pos, pos_type=args.pos_type, page_range=args.page_range, output_path=args.output)
    elif args.which == "replace":
        replace_pdf(doc_path1=args.input_path1, doc_path2=args.input_path2, src_range=args.src_page_range, dst_range=args.dst_page_range, output_path=args.output)
    elif args.which == "reorder":
        reorder_pdf(doc_path=args.input_path, page_range=args.page_range, output_path=args.output)
    elif args.which == "rotate":
        rotate_pdf(doc_path=args.input_path, angle=args.angle, page_range=args.page_range, output_path=args.output)
    elif args.which == "encrypt":
        encrypt_pdf(doc_path=args.input_path, user_password=args.user_password, owner_password=args.owner_password, perm=args.perm, output_path=args.output)
    elif args.which == "decrypt":
        decrypt_pdf(doc_path=args.input_path, password=args.password, output_path=args.output)
    elif args.which == "compress":
        compress_pdf(doc_path=args.input_path, output_path=args.output)
    elif args.which == "resize":
        if args.method == "dim":
            resize_pdf_by_dim(doc_path=args.input_path, width=args.width, height=args.height, unit=args.unit, page_range=args.page_range, output_path=args.output)
        elif args.method == "scale":
            resize_pdf_by_scale(doc_path=args.input_path, scale=args.scale, page_range=args.page_range, output_path=args.output)
        elif args.method == "paper_size":
            resize_pdf_by_paper_size(doc_path=args.input_path, paper_size=args.paper_size, page_range=args.page_range, output_path=args.output)
    elif args.which == "bookmark":
        if args.bookmark_which == "add":
            if args.method == "file":
                add_toc_from_file(toc_path=args.toc, doc_path=args.input_path, offset=args.offset, output_path=args.output)
            elif args.method == "gap":
                add_toc_by_gap(doc_path=args.input_path, gap=args.gap, format=args.format, output_path=args.output)
        elif args.bookmark_which == "extract":
            extract_toc(doc_path=args.input_path, format=args.format, output_path=args.output)
        elif args.bookmark_which == "transform":
            level_dict_list = []
            if args.level_dict:
                for item in args.level_dict:
                    level_dict = eval(item)
                    level_dict_list.append(level_dict)
            transform_toc_file(toc_path=args.toc, level_dict_list=level_dict_list, delete_level_below=args.delete_level_below, add_offset=args.add_offset, default_level=args.default_level, is_remove_blanklines=args.remove_blank_lines, output_path=args.output)
    elif args.which == "extract":
        if args.type == "text":
            extract_pdf_text(doc_path=args.input_path, page_range=args.page_range, output_path=args.output)
        elif args.type == "image":
            extract_pdf_images(doc_path=args.input_path, page_range=args.page_range, output_path=args.output)
        else:
            raise ValueError("不支持的提取类型!")
    elif args.which == "cut":
        if args.method == "grid":
            cut_pdf_by_grid(doc_path=args.input_path, n_row=args.nrow, n_col=args.ncol, page_range=args.page_range, output_path=args.output)
        elif args.method == "breakpoints":
            cut_pdf_by_breakpoints(doc_path=args.input_path, h_breakpoints=args.h_breakpoints, v_breakpoints=args.v_breakpoints, page_range=args.page_range, output_path=args.output)
    elif args.which == "combine":
        combine_pdf_by_grid(doc_path=args.input_path, n_row=args.nrow, n_col=args.ncol, paper_size=args.paper_size, orientation=args.orientation, page_range=args.page_range, output_path=args.output)
    elif args.which == "crop":
        if args.method == "bbox":
            crop_pdf_by_bbox(doc_path=args.input_path, bbox=args.bbox, unit=args.unit, keep_page_size=args.keep_size, page_range=args.page_range, output_path=args.output)
        elif args.method == "margin":
            crop_pdf_by_page_margin(doc_path=args.input_path, margin=args.margin, unit=args.unit, keep_page_size=args.keep_size, page_range=args.page_range, output_path=args.output)
    elif args.which == "convert":
        if args.source_type == "pdf":
            if args.target_type == "png":
                convert_pdf2png(doc_path=args.input_path, dpi=args.dpi, page_range=args.page_range,output_path=args.output)
            elif args.target_type == "svg":
                convert_pdf2svg(doc_path=args.input_path, dpi=args.dpi, page_range=args.page_range,output_path=args.output)
            elif args.target_type == "image-pdf":
                convert_to_image_pdf(doc_path=args.input_path, dpi=args.dpi, page_range=args.page_range,output_path=args.output)
        elif args.target_type == "pdf":
            if args.source_type == "png":
                convert_png2pdf(input_path=args.input_path, is_merge=args.is_merge,output_path=args.output)
            elif args.source_type == "svg":
                convert_svg2pdf(input_path=args.input_path, is_merge=args.is_merge,output_path=args.output)
            elif args.source_type == "mobi":
                convert_anydoc2pdf(input_path=args.input_path, output_path=args.output)
            elif args.source_type == "equb":
                convert_anydoc2pdf(input_path=args.input_path, output_path=args.output)
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
    elif args.which == "mask":
        if args.type == "rect":
            mask_pdf_by_rectangle(doc_path=args.input_path, bbox_list=args.bbox, color=args.color, opacity=args.opacity, angle=args.angle, unit=args.unit, page_range=args.page_range, output_path=args.output)
        elif args.type == "annot":
            mask_pdf_by_rectangle_annot(doc_path=args.input_path, annot_page=args.annot_page, color=args.color, opacity=args.opacity, angle=args.angle, page_range=args.page_range, output_path=args.output)
    elif args.which == "bg":
        if args.type == "color":
            add_doc_background_by_color(doc_path=args.input_path, color=args.color, opacity=args.opacity, angle=args.angle, x_offset=args.x_offset, y_offset=args.y_offset, page_range=args.page_range, output_path=args.output)
        elif args.type == "image":
            add_doc_background_by_image(doc_path=args.input_path, img_path=args.img_path, opacity=args.opacity, angle=args.angle, x_offset=args.x_offset, y_offset=args.y_offset, scale=args.scale, page_range=args.page_range, output_path=args.output)
    elif args.which == "header_footer":
        if args.type == "add":
            content_list = [args.header_left, args.header_center, args.header_right, args.footer_left, args.footer_center, args.footer_right]
            insert_header_and_footer(doc_path=args.input_path, content_list=content_list, font_family=args.font_family, font_size=args.font_size, font_color=args.font_color, opacity=args.opacity, margin_bbox=args.margin_bbox, page_range=args.page_range, unit=args.unit, output_path=args.output)
        elif args.type == "remove":
            remove_header_and_footer(doc_path=args.input_path, margin_bbox=args.margin_bbox, remove_list=args.remove, unit=args.unit, page_range=args.page_range, output_path=args.output)
    elif args.which == "page_number":
        if args.type == "add":
            insert_page_number(doc_path=args.input_path, format=args.format, pos=args.pos, start=args.start, margin_bbox=args.margin_bbox, font_family=args.font_family, font_size=args.font_size, font_color=args.font_color, opacity=args.opacity, align=args.align, page_range=args.page_range, unit=args.unit, output_path=args.output)
        elif args.type == "remove":
            remove_page_number(doc_path=args.input_path, margin_bbox=args.margin_bbox, pos=args.pos, unit=args.unit, page_range=args.page_range, output_path=args.output)
    elif args.which == "dual":
        if args.input_path.lower().endswith(".pdf"):
            make_dual_layer_pdf(input_path=args.input_path, dpi=args.dpi, page_range=args.page_range, lang=args.lang, output_path=args.output)
        elif args.input_path.lower().endswith(".png") or args.input_path.lower().endswith(".jpg") or args.input_path.lower().endswith(".jpeg"):
            make_dual_layer_pdf_from_image(doc_path=args.input_path, lang=args.lang, output_path=args.output)
        else:
            raise ValueError("不支持的文件类型!")

if __name__ == "__main__":
    main()
