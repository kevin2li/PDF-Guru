import traceback
from pathlib import Path

import fitz
import utils
from constants import cmd_output_path
from loguru import logger


@utils.batch_process()
def extract_pdf_images(doc_path: str, page_range: str = "all", output_path: str = None):
    try:
        doc: fitz.Document = fitz.open(doc_path)
        roi_indicies = utils.parse_range(page_range, doc.page_count)
        if output_path is None:
            p = Path(doc_path)
            output_path = str(p.parent / f"{p.stem}-图片")
            Path(output_path).mkdir(parents=True, exist_ok=True)
        else:
            Path(output_path).mkdir(parents=True, exist_ok=True)
        for page_index in roi_indicies:
            page = doc[page_index]
            image_list = page.get_images()
            for i, img in enumerate(image_list):
                xref = img[0] # get the XREF of the image
                pix = fitz.Pixmap(doc, xref) # create a Pixmap
                if pix.n - pix.alpha > 3: # CMYK: convert to RGB first
                    pix = fitz.Pixmap(fitz.csRGB, pix)
                savepath = str(Path(output_path) / f"{page_index+1}-{i+1}.png")
                pix.save(savepath) # save the image as PNG
                pix = None
        utils.dump_json(cmd_output_path, {"status": "success", "message": ""})
    except:
        logger.error(traceback.format_exc())
        utils.dump_json(cmd_output_path, {"status": "error", "message": traceback.format_exc()})

@utils.batch_process()
def extract_pdf_text(doc_path: str, page_range: str = "all", output_path: str = None):
    try:
        doc: fitz.Document = fitz.open(doc_path)
        roi_indicies = utils.parse_range(page_range, doc.page_count)
        if output_path is None:
            p = Path(doc_path)
            output_path = str(p.parent / f"{p.stem}-文本")
            Path(output_path).mkdir(parents=True, exist_ok=True)
        else:
            Path(output_path).mkdir(parents=True, exist_ok=True)
        for page_index in roi_indicies:
            page = doc[page_index]
            text = page.get_text()
            savepath = str(Path(output_path) / f"{page_index+1}.txt")
            with open(savepath, "w", encoding="utf-8") as f:
                f.write(text)
        utils.dump_json(cmd_output_path, {"status": "success", "message": ""})
    except:
        logger.error(traceback.format_exc())
        utils.dump_json(cmd_output_path, {"status": "error", "message": traceback.format_exc()})
