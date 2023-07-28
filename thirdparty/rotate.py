import traceback
from pathlib import Path

import fitz
import utils
from constants import cmd_output_path
from loguru import logger


@utils.batch_process()
def rotate_pdf(doc_path: str, angle: int, page_range: str = "all", output_path: str = None):
    try:
        doc: fitz.Document = fitz.open(doc_path)
        roi_indices = utils.parse_range(page_range, doc.page_count)
        for page_index in roi_indices:
            page = doc[page_index]
            page.set_rotation(angle)
            
        if output_path is None:
            p = Path(doc_path)
            output_path = str(p.parent / f"{p.stem}-旋转.pdf")
        doc.save(output_path, garbage=3, deflate=True)
        utils.dump_json(cmd_output_path, {"status": "success", "message": ""})
    except:
        logger.error(traceback.format_exc())
        utils.dump_json(cmd_output_path, {"status": "error", "message": traceback.format_exc()})
