import traceback
from pathlib import Path
from typing import Tuple

import fitz
import utils
from constants import cmd_output_path
from loguru import logger

@utils.batch_process()
def crop_pdf_by_bbox(doc_path: str, bbox: Tuple[int, int, int, int], unit: str = "pt", keep_page_size: bool = True, page_range: str = "all", output_path: str = None):
    try:
        doc: fitz.Document = fitz.open(doc_path)
        roi_indices = utils.parse_range(page_range, doc.page_count)
        writer: fitz.Document = fitz.open()
        if unit != "pt":
            bbox = tuple(map(lambda x: utils.convert_length(x, unit, "pt"), bbox))
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
        utils.dump_json(cmd_output_path, {"status": "success", "message": ""})
    except:
        logger.error(traceback.format_exc())
        utils.dump_json(cmd_output_path, {"status": "error", "message": traceback.format_exc()})

@utils.batch_process()
def crop_pdf_by_page_margin(doc_path: str, margin: Tuple[int, int, int, int], unit: str = "pt", keep_page_size: bool = True, page_range: str = "all", output_path: str = None):
    try:
        doc: fitz.Document = fitz.open(doc_path)
        roi_indices = utils.parse_range(page_range, doc.page_count)
        writer: fitz.Document = fitz.open()
        if unit != "pt":
            margin = tuple(map(lambda x: utils.convert_length(x, unit, "pt"), margin))
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
        utils.dump_json(cmd_output_path, {"status": "success", "message": ""})
    except:
        logger.error(traceback.format_exc())
        utils.dump_json(cmd_output_path, {"status": "error", "message": traceback.format_exc()})

def crop_pdf_by_rect_annot(doc_path: str,  keep_page_size: bool = True, page_range: str = "all", output_path: str = None):
    try:
        doc: fitz.Document = fitz.open(doc_path)
        roi_indices = utils.parse_range(page_range, doc.page_count)
        writer: fitz.Document = fitz.open()
        FLAG = False
        for page_index in roi_indices:
            page = doc[page_index]
            rect_list = []
            for annot in page.annots():
                if annot.type[0] == 4: # Square
                    rect_list.append(annot.rect)
                page.delete_annot(annot)
            logger.debug(rect_list)
            if rect_list:
                FLAG = True
                page_width, page_height = page.rect.width, page.rect.height
                for rect in rect_list:
                    if keep_page_size:
                        new_page = writer.new_page(-1, width=page_width, height=page_height)
                        new_page.show_pdf_page(new_page.rect, doc, page_index, clip=rect)
                    else:
                        new_page = writer.new_page(-1, width=rect[2]-rect[0], height=rect[3]-rect[1])
                        new_page.show_pdf_page(new_page.rect, doc, page_index, clip=rect)
        if not FLAG:
            utils.dump_json(cmd_output_path, {"status": "error", "message": "未找到矩形标注!"})
            return
        if output_path is None:
            p = Path(doc_path)
            output_path = str(p.parent / f"{p.stem}-注释裁剪.pdf")
        writer.save(output_path, garbage=3, deflate=True)
    except:
        logger.error(traceback.format_exc())
        utils.dump_json(cmd_output_path, {"status": "error", "message": traceback.format_exc()})
