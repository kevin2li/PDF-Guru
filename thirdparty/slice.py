import traceback
from pathlib import Path
from typing import Tuple

import fitz
import utils
from constants import cmd_output_path
from loguru import logger

@utils.batch_process()
def slice_pdf(doc_path: str, page_range: str = "all", output_path: str = None, is_reverse: bool = False):
    try:
        doc: fitz.Document = fitz.open(doc_path)
        p = Path(doc_path)
        if output_path is None:
            output_dir = p.parent
        roi_indices = utils.parse_range(page_range, doc.page_count, is_reverse=is_reverse)
        writer: fitz.Document = fitz.open()
        parts = utils.range_compress(roi_indices)
        for part in parts:
            writer.insert_pdf(doc, from_page=part[0], to_page=part[1])
        writer.save(str(output_dir / f"{p.stem}-切片.pdf"), garbage=3, deflate=True)
        utils.dump_json(cmd_output_path, {"status": "success", "message": ""})
    except:
        logger.error(f"roi_indices: {roi_indices}")
        logger.error(traceback.format_exc())
        utils.dump_json(cmd_output_path, {"status": "error", "message": traceback.format_exc()})


@utils.batch_process()
def reorder_pdf(doc_path: str, page_range: str = "all", output_path: str = None):
    try:
        doc: fitz.Document = fitz.open(doc_path)
        p = Path(doc_path)
        roi_indices = utils.parse_range(page_range, doc.page_count, is_unique=False)
        if output_path is None:
            output_path = str(p.parent / f"{p.stem}-重排.pdf")
        writer: fitz.Document = fitz.open()
        for i in roi_indices:
            writer.insert_pdf(doc, from_page=i, to_page=i)
        writer.save(output_path, garbage=3, deflate=True)
        utils.dump_json(cmd_output_path, {"status": "success", "message": ""})
    except:
        logger.error(traceback.format_exc())
        utils.dump_json(cmd_output_path, {"status": "error", "message": traceback.format_exc()})
