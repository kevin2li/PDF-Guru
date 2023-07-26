import traceback
from pathlib import Path

import fitz
import utils
from constants import cmd_output_path
from loguru import logger

@utils.batch_process()
def resize_pdf_by_dim(doc_path: str, width: float, height: float, unit: str = "pt", page_range: str = "all", output_path: str = None):
    try:
        doc: fitz.Document = fitz.open(doc_path)
        writer: fitz.Document = fitz.open()
        width, height = utils.convert_length(width, unit, "pt"), utils.convert_length(height, unit, "pt")
        roi_indices = utils.parse_range(page_range, doc.page_count)
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
        utils.dump_json(cmd_output_path, {"status": "success", "message": ""})
    except:
        logger.error(traceback.format_exc())
        utils.dump_json(cmd_output_path, {"status": "error", "message": traceback.format_exc()})

@utils.batch_process()
def resize_pdf_by_scale(doc_path: str, scale: float, page_range: str = "all", output_path: str = None):
    try:
        doc: fitz.Document = fitz.open(doc_path)
        writer: fitz.Document = fitz.open()
        roi_indices = utils.parse_range(page_range, doc.page_count)
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
        utils.dump_json(cmd_output_path, {"status": "success", "message": ""})
    except:
        logger.error(traceback.format_exc())
        utils.dump_json(cmd_output_path, {"status": "error", "message": traceback.format_exc()})

@utils.batch_process()
def resize_pdf_by_paper_size(doc_path: str, paper_size: str, page_range: str = "all", output_path: str = None):
    try:
        doc: fitz.Document = fitz.open(doc_path)
        writer: fitz.Document = fitz.open()
        roi_indices = utils.parse_range(page_range, doc.page_count)
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
        utils.dump_json(cmd_output_path, {"status": "success", "message": ""})
    except:
        logger.error(traceback.format_exc())
        utils.dump_json(cmd_output_path, {"status": "error", "message": traceback.format_exc()})
