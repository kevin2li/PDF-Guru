import glob
import re
import traceback
from pathlib import Path

import fitz
import argparse

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

def batch_process(func):
    def wrapper(*args, **kwargs):
        print(f"args: {args}")
        print(f"kwargs: {kwargs}")
        doc_path = kwargs['doc_path']
        if "*" in doc_path:
            path_list = glob.glob(doc_path)
            print.debug(f"path_list length: {len(path_list) if path_list else 0}")
            if path_list:
                del kwargs['doc_path']
                for path in path_list:
                    func(*args, doc_path=path, **kwargs)
        else:
            func(*args, **kwargs)
        func(*args, **kwargs)
    return wrapper

@batch_process
def convert_docx2pdf(doc_path: str, output_path: str = None):
    try:
        from docx2pdf import convert
        if output_path is None:
            p = Path(doc_path)
            output_path = str(p.parent / f"{p.stem}.pdf")
        convert(doc_path, output_path)
    except:
        raise ValueError(traceback.format_exc())

@batch_process
def convert_pdf2docx(doc_path: str, page_range: str = "all", output_path: str = None):
    try:
        from pdf2docx import Converter
        doc = fitz.open(doc_path)
        roi_indices = parse_range(page_range, doc.page_count)
        cv = Converter(doc_path)
        if output_path is None:
            p = Path(doc_path)
            output_path = str(p.parent / f"{p.stem}.docx")
        cv.convert(output_path, pages=roi_indices)
        cv.close()
    except:
        raise ValueError(traceback.format_exc())

def main():
    parser = argparse.ArgumentParser(description="Convert functions")
    parser.add_argument("input_path", type=str, help="pdf文件路径")
    parser.add_argument("--source-type", type=str, choices=["pdf", 'png', "jpg", "svg", "docx"], default="pdf", help="源类型")
    parser.add_argument("--target-type", type=str, choices=['png', "svg", "docx"], default="png", help="目标类型")
    parser.add_argument("--page_range", type=str, default="all", help="页码范围")
    parser.add_argument("-o", "--output", type=str, help="输出文件路径")
    args = parser.parse_args()
    if args.source_type == "pdf":
        if args.target_type == "docx":
            convert_pdf2docx(doc_path=args.input_path, page_range=args.page_range, output_path=args.output)

if __name__ == '__main__':
    main()