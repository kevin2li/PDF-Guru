import traceback
from pathlib import Path

import fitz
import utils
from constants import cmd_output_path
from loguru import logger

@utils.batch_process()
def compress_pdf(doc_path: str, output_path: str = None):
    try:
        doc: fitz.Document = fitz.open(doc_path)
        p = Path(doc_path)
        if output_path is None:
            output_path = str(p.parent / f"{p.stem}-压缩.pdf")
        doc.save(output_path, garbage=4, deflate=True, clean=True)
        utils.dump_json(cmd_output_path, {"status": "success", "message": ""})
    except:
        logger.error(traceback.format_exc())
        utils.dump_json(cmd_output_path, {"status": "error", "message": traceback.format_exc()})
