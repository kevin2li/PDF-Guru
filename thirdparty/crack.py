import traceback

import fitz
import utils
from constants import cmd_output_path
from loguru import logger

def extract_encrypt_pdf_hash(doc_path: str):
    try:
        doc: fitz.Document = fitz.open(doc_path)
        out = doc.metadata
        logger.debug(out)
        xreflen = doc.xref_length()  # length of objects table
        for xref in range(1, xreflen):  # skip item 0!
                print("")
                print("object %i (stream: %s)" % (xref, doc.xref_is_stream(xref)))
                print(doc.xref_object(xref, compressed=False))
    except:
        logger.error(traceback.format_exc())
        utils.dump_json(cmd_output_path, {"status": "error", "message": traceback.format_exc()})
