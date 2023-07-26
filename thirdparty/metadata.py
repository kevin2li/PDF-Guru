import traceback

import fitz
import utils
from constants import cmd_output_path
from loguru import logger

def extract_metadata(doc_path: str, output_path: str = None):
    try:
        doc: fitz.Document = fitz.open(doc_path)
        out = doc.metadata
        logger.debug(out)
        # embfile_info = doc.embfile_info()
        # logger.debug(embfile_info)

        out = doc.chapter_count
        logger.debug(out)

        catalog = doc.pdf_catalog()
        logger.debug(catalog)

        perm = doc.permissions
        logger.debug(perm)

        metadata = {}  # make my own metadata dict
        what, value = doc.xref_get_key(-1, "Info")  # /Info key in the trailer
        if what != "xref":
            pass  # PDF has no metadata
        else:
            xref = int(value.replace("0 R", ""))  # extract the metadata xref
            for key in doc.xref_get_keys(xref):
                metadata[key] = doc.xref_get_key(xref, key)[1]
        metadata['page_count'] = doc.page_count
        page_size = doc[-1].rect
        metadata['page_size'] = (utils.convert_length(page_size.width, "pt", "cm"), utils.convert_length(page_size.height, "pt", "cm"))
        file_size = os.path.getsize(doc_path)
        metadata['file_size'] = utils.human_readable_size(file_size)
        logger.debug(metadata)
        utils.dump_json(cmd_output_path, {"status": "success", "message": ""})
    except:
        logger.error(traceback.format_exc())
        utils.dump_json(cmd_output_path, {"status": "error", "message": traceback.format_exc()})

