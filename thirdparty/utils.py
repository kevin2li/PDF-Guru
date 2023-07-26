# 工具类函数
import colorsys
import functools
import glob
import json
import re

from loguru import logger


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

def contains_rect(rect1, rect2) -> bool:
    x1, y1, x2, y2 = rect1
    x3, y3, x4, y4 = rect2
    if x1 <= x3 and y1 <= y3 and x2 >= x4 and y2 >= y4:
        return True
    return False

def batch_process(field: str = "doc_path"):
    def decorator(func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            logger.debug(args)
            logger.debug(kwargs)
            doc_path = kwargs[field]
            if "*" in doc_path:
                path_list = glob.glob(doc_path)
                logger.debug(f"path_list length: {len(path_list) if path_list else 0}")
                if path_list:
                    for path in path_list:
                        kwargs[field] = path
                        func(*args, **kwargs)
            else:
                func(*args, **kwargs)
        return wrapper
    return decorator
