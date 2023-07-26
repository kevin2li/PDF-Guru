import fitz
from pathlib import Path
import utils
from constants import cmd_output_path
from loguru import logger
import traceback
import re

@utils.batch_process()
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
        utils.dump_json(cmd_output_path, {"status": "success", "message": ""})
    except:
        logger.error(traceback.format_exc())
        utils.dump_json(cmd_output_path, {"status": "error", "message": traceback.format_exc()})

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
        doc2_indices = utils.parse_range(page_range, n2)
        for i in doc2_indices:
            writer.insert_pdf(doc2, from_page=i, to_page=i)
        if insert_pos-1 < n1:
            writer.insert_pdf(doc1, from_page=insert_pos-1, to_page=n1-1)
        writer.save(output_path, garbage=3, deflate=True, incremental=doc_path1==output_path)
        utils.dump_json(cmd_output_path, {"status": "success", "message": ""})
    except:
        logger.error(traceback.format_exc())
        utils.dump_json(cmd_output_path, {"status": "error", "message": traceback.format_exc()})

def replace_pdf(doc_path1: str, doc_path2: str, src_range: str = "all", dst_range: str = "all", output_path: str = None):
    try:
        doc1: fitz.Document = fitz.open(doc_path1)
        doc2: fitz.Document = fitz.open(doc_path2)
        src_range = src_range.strip()
        dst_range = dst_range.strip()
        n1, n2 = doc1.page_count, doc2.page_count
        if re.match("^!?(\d+|N)(\-(\d+|N))?$", src_range) is None:
            logger.error(f"src_range: {src_range}, 源页码格式错误")
            utils.dump_json(cmd_output_path, {"status": "error", "message": "源页码格式错误!"})
            return
        if output_path is None:
            p = Path(doc_path1)
            output_path = str(p.parent / f"{p.stem}-替换.pdf")
        writer: fitz.Document = fitz.open()
        dst_indices = utils.parse_range(dst_range, n2)
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
            writer.save(output_path, garbage=3, deflate=True, incremental=doc_path1==output_path)
        elif len(parts) == 1:
            a = int(parts[0]) if parts[0] != "N" else n1
            if a-2 >= 0:
                writer.insert_pdf(doc1, from_page=0, to_page=a-2)
            for i in dst_indices:
                writer.insert_pdf(doc2, from_page=i, to_page=i)
            if a < n1:
                writer.insert_pdf(doc1, from_page=a, to_page=n1-1)
            writer.save(output_path, garbage=3, deflate=True, incremental=doc_path1==output_path)
        else:
            logger.error("页码格式错误")
            utils.dump_json(cmd_output_path, {"status": "error", "message": "页码格式错误!"})
            return
        utils.dump_json(cmd_output_path, {"status": "success", "message": ""})
    except:
        logger.error(traceback.format_exc())
        utils.dump_json(cmd_output_path, {"status": "error", "message": traceback.format_exc()})
