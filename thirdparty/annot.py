import glob
import re
import traceback
from pathlib import Path
from typing import List

import fitz
import utils
from constants import cmd_output_path
from loguru import logger

annot_type_code = {
    fitz.PDF_ANNOT_HIGHLIGHT: 'highlight',
    fitz.PDF_ANNOT_INK: 'ink',
    fitz.PDF_ANNOT_SQUARE: 'square',
    fitz.PDF_ANNOT_CIRCLE: 'oval',
    fitz.PDF_ANNOT_STRIKE_OUT: 'strikeout',
    fitz.PDF_ANNOT_UNDERLINE: 'underline',
    fitz.PDF_ANNOT_SQUIGGLY: 'squiggly',
    fitz.PDF_ANNOT_POLYGON: 'polygon',
    fitz.PDF_ANNOT_POLY_LINE: 'polyline',
    fitz.PDF_ANNOT_CARET: 'caret',
    fitz.PDF_ANNOT_REDACT: 'redact',
    fitz.PDF_ANNOT_LINE: 'line',
    fitz.PDF_ANNOT_TEXT: 'text',
    fitz.PDF_ANNOT_WIDGET: 'widget',
    fitz.PDF_ANNOT_LINK: 'link',
    fitz.PDF_ANNOT_SOUND: 'sound',
    fitz.PDF_ANNOT_MOVIE: 'movie',
    fitz.PDF_ANNOT_SCREEN: 'screen',
    fitz.PDF_ANNOT_PRINTER_MARK: 'printermark',
    fitz.PDF_ANNOT_FILE_ATTACHMENT: 'fileattachment',
    fitz.PDF_ANNOT_FREE_TEXT: 'freetext',
    fitz.PDF_ANNOT_STAMP: 'stamp',
    fitz.PDF_ANNOT_POPUP: 'popup',
    fitz.PDF_ANNOT_WATERMARK: 'watermark',
    fitz.PDF_ANNOT_3D: '3d',
}

def delete_annot_pdf(doc_path: str, annot_types: List[str] = [], page_range: str = "all", output_path: str = None):
    try:
        doc: fitz.Document = fitz.open(doc_path)
        roi_indices = utils.parse_range(page_range, doc.page_count)
        for page_index in roi_indices:
            page = doc[page_index]
            for annot in page.annots():
                logger.debug(annot)
                if "all" in annot_types:
                    page.delete_annot(annot)
                else:
                    if annot_type_code.get(annot.type[0]) in annot_types:
                        page.delete_annot(annot)
        if output_path is None:
            p = Path(doc_path)
            output_path = str(p.parent / f"{p.stem}-删除批注.pdf")
        doc.save(output_path, garbage=3, deflate=True)
        utils.dump_json(cmd_output_path, {"status": "success", "message": ""})
    except:
        logger.error(traceback.format_exc())
        utils.dump_json(cmd_output_path, {"status": "error", "message": traceback.format_exc()})
