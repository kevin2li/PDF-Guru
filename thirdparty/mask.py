import traceback
from pathlib import Path
from typing import List

import fitz
import utils
from constants import cmd_output_path
from loguru import logger
from reportlab.pdfgen import canvas


@utils.batch_process()
def mask_pdf_by_rectangle(
        doc_path   : str,
        bbox_list  : List[List[float]],
        color      : str = "#FFFFFF",
        opacity    : float = 1,
        angle      : float = 0,
        overlay    : bool = True,
        page_range : str = "all",
        unit       : str = "pt",
        output_path: str = None
    ):
    try:
        doc: fitz.Document = fitz.open(doc_path)
        width, height = doc[-1].rect.width, doc[-1].rect.height
        p = Path(doc_path)
        mask_doc_path = str(p.parent / "tmp_mask.pdf")
        c = canvas.Canvas(mask_doc_path,pagesize=(width, height))
        color = [v/255. for v in utils.hex_to_rgb(color)]
        logger.debug(bbox_list)
        logger.debug(doc[-1].rect)
        for bbox in bbox_list:
            bbox = [utils.convert_length(x, unit, "pt") for x in bbox]
            bbox[1], bbox[3] = height-bbox[1], height-bbox[3]
            c.setStrokeColorRGB(*color)
            c.setFillColorRGB(*color)
            c.setFillAlpha(opacity)
            c.rotate(angle)
            box_w, box_h = bbox[2]-bbox[0], bbox[3]-bbox[1]
            c.rect(bbox[0], bbox[1], box_w, box_h, fill=True, stroke=False)
        c.showPage()
        c.save()

        mask_doc: fitz.Document = fitz.open(mask_doc_path)
        roi_indicies = utils.parse_range(page_range, doc.page_count)
        for page_index in range(doc.page_count):
            page = doc[page_index]
            if page_index in roi_indicies:
                page.show_pdf_page(page.rect, mask_doc, 0, overlay=overlay)
                page.clean_contents()
        if output_path is None:
            output_path = str(p.parent / f"{p.stem}-加遮罩.pdf")
        doc.save(output_path, garbage=3, deflate=True)
        doc.close()
        mask_doc.close()
        os.remove(mask_doc_path)
        utils.dump_json(cmd_output_path, {"status": "success", "message": ""})
    except:
        logger.error(traceback.format_exc())
        utils.dump_json(cmd_output_path, {"status": "error", "message": traceback.format_exc()})

@utils.batch_process()
def mask_pdf_by_rectangle_annot(
        doc_path   : str,
        annot_page : int = 0,
        color      : str = "#FFFFFF",
        opacity    : float = 1,
        angle      : float = 0,
        page_range : str = "all",
        output_path: str = None
    ):
    try:
        doc: fitz.Document = fitz.open(doc_path)
        page = doc[annot_page]
        rect_list = []
        for annot in page.annots():
            if annot.type[0] == 4: # Square
                rect_list.append(annot.rect)
            page.delete_annot(annot)
        logger.debug(rect_list)
        if rect_list:
            p = Path(doc_path)
            clean_doc_path = str(p.parent / "tmp_clean.pdf")
            doc.save(clean_doc_path, garbage=3, deflate=True)
            if output_path is None:
                output_path = str(p.parent / f"{p.stem}-批注遮罩版.pdf")
            mask_pdf_by_rectangle(doc_path=clean_doc_path, bbox_list=rect_list, color=color, opacity=opacity, angle=angle, page_range=page_range, output_path=output_path)
            os.remove(clean_doc_path)
        else:
            logger.error("没有找到矩形注释!")
            utils.dump_json(cmd_output_path, {"status": "error", "message": "没有找到矩形注释!"})
            return
        utils.dump_json(cmd_output_path, {"status": "success", "message": ""})
    except:
        logger.error(traceback.format_exc())
        utils.dump_json(cmd_output_path, {"status": "error", "message": traceback.format_exc()})
