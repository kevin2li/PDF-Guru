import os
import traceback
from pathlib import Path

import fitz
import utils
from constants import cmd_output_path
from loguru import logger
from PIL import Image
from reportlab.pdfgen import canvas


@utils.batch_process()
def add_doc_background_by_color(
        doc_path   : str,
        color      : str = "#FFFFFF",
        opacity    : float = 1,
        angle      : float = 0,
        x_offset   : float = 0,
        y_offset   : float = 0,
        page_range : str = "all",
        output_path: str = None
    ):
    try:
        doc: fitz.Document = fitz.open(doc_path)
        color = [v/255. for v in utils.hex_to_rgb(color)]
        width = doc[-1].rect.width
        height = doc[-1].rect.height
        logger.debug(doc[-1].rect)
        p = Path(doc_path)
        bg_output_path = str(p.parent / "tmp_bg.pdf")
        c = canvas.Canvas(bg_output_path, pagesize=(width, height))
        c.setStrokeColorRGB(*color)
        c.setFillColorRGB(*color)
        c.setFillAlpha(opacity)
        c.translate(width/2, height/2)
        c.rotate(angle)
        c.rect(-width/2+x_offset, -height/2+y_offset, width, height, fill=True, stroke=False)
        c.showPage()
        c.save()
        
        bg_doc = fitz.open(bg_output_path)
        roi_indicies = utils.parse_range(page_range, doc.page_count)
        for page_index in range(doc.page_count):
            page = doc[page_index]
            if page_index in roi_indicies:
                page.show_pdf_page(page.rect, bg_doc, 0, overlay=False)
                page.clean_contents()
        if output_path is None:
            output_path = str(p.parent / f"{p.stem}-加背景.pdf")
        doc.save(output_path, garbage=3, deflate=True)
        doc.close()
        bg_doc.close()
        os.remove(bg_output_path)
        utils.dump_json(cmd_output_path, {"status": "success", "message": ""})
    except:
        logger.error(traceback.format_exc())
        utils.dump_json(cmd_output_path, {"status": "error", "message": traceback.format_exc()})

@utils.batch_process()
def add_doc_background_by_image(
        doc_path   : str,
        img_path   : str,
        opacity    : float = 1,
        angle      : float = 0,
        x_offset   : float = 0,
        y_offset   : float = 0,
        scale      : float = 1,
        page_range : str = "all",
        output_path: str = None
    ):
    try:
        doc: fitz.Document = fitz.open(doc_path)
        width = doc[-1].rect.width
        height = doc[-1].rect.height
        logger.debug(doc[-1].rect)
        p = Path(doc_path)
        bg_output_path = str(p.parent / "tmp_bg.pdf")
        
        c = canvas.Canvas(bg_output_path, pagesize=(width, height))
        c.setFillAlpha(opacity)
        c.translate(width/2, height/2)
        c.rotate(angle)
        img = Image.open(img_path)
        img_width, img_height = img.size
        scaled_w, scaled_h = img_width*scale, img_height*scale
        c.drawImage(img_path, -scaled_w/2+x_offset, -scaled_h/2+y_offset, width=scaled_w, height=scaled_h)
        c.showPage()
        c.save()

        bg_doc = fitz.open(bg_output_path)
        roi_indicies = utils.parse_range(page_range, doc.page_count)
        for page_index in range(doc.page_count):
            page = doc[page_index]
            if page_index in roi_indicies:
                page.show_pdf_page(page.rect, bg_doc, 0, overlay=False)
                page.clean_contents()
        if output_path is None:
            output_path = str(p.parent / f"{p.stem}-加背景.pdf")
        doc.save(output_path, garbage=3, deflate=True)
        doc.close()
        bg_doc.close()
        os.remove(bg_output_path)
        utils.dump_json(cmd_output_path, {"status": "success", "message": ""})
    except:
        logger.error(traceback.format_exc())
        utils.dump_json(cmd_output_path, {"status": "error", "message": traceback.format_exc()})
