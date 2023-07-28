import os
import traceback
from pathlib import Path
from typing import List

import fitz
import utils
from constants import cmd_output_path
from loguru import logger
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.pdfgen import canvas


def create_header_and_footer_mask(
        width       : float,
        height      : float,
        content_list: List[str],
        margin_bbox : List[float] = [1.27, 1.27, 2.54, 2.54], # [top, bottom, left, right]
        font_family : str = "msyh.ttc",
        font_size   : float = 11,
        font_color  : str = "#000000",
        opacity     : str = 1,
        unit        : str = "cm",
        output_path : str = None
):
    try:
        if output_path is None:
            output_path = "tmp_hf.pdf"
        c = canvas.Canvas(output_path,pagesize=(width, height))
        fontpath = str(Path(os.environ['WINDIR']) / "fonts" / font_family)
        pdfmetrics.registerFont(TTFont('custom_font', fontpath))
        font_color = [v/255. for v in utils.hex_to_rgb(font_color)]
        margin_bbox = [utils.convert_length(x, unit, "pt") for x in margin_bbox]
        c.setFont("custom_font", font_size)
        c.setStrokeColorRGB(*font_color)
        c.setFillColorRGB(*font_color)
        c.setFillAlpha(opacity)
        c.setLineWidth(width-margin_bbox[3]-margin_bbox[2])
        for i, content in enumerate(content_list):
            if content.strip() == "":
                continue
            parts = content.split("\n")
            string_height = c.stringWidth(parts[0][0], "custom_font", font_size)
            if i < 3: # 页眉
                parts = parts[::-1]
                if i == 0:
                    for j, part in enumerate(parts):
                        c.drawString(margin_bbox[2], height-margin_bbox[0]+j*string_height, part)
                elif i == 1:
                    for j, part in enumerate(parts):
                        c.drawCentredString(width/2, height-margin_bbox[0]+j*string_height, part)
                elif i == 2:
                    for j, part in enumerate(parts):
                        c.drawRightString(width-margin_bbox[3], height-margin_bbox[0]+j*string_height, part)
            else: # 页脚
                if i == 3:
                    for j, part in enumerate(parts, 1):
                        c.drawString(margin_bbox[2], margin_bbox[1]-j*string_height, part)
                elif i == 4:
                    for j, part in enumerate(parts, 1):
                        c.drawCentredString(width/2, margin_bbox[1]-j*string_height, part)
                elif i == 5:
                    for j, part in enumerate(parts, 1):
                        c.drawRightString(width-margin_bbox[3], margin_bbox[1]-j*string_height, part)
        c.showPage()
        c.save()
        utils.dump_json(cmd_output_path, {"status": "success", "message": ""})
    except:
        logger.error(traceback.format_exc())
        utils.dump_json(cmd_output_path, {"status": "error", "message": traceback.format_exc()})

@utils.batch_process()
def insert_header_and_footer(
        doc_path   : str,
        content_list    : List[str],
        margin_bbox: List[float] = [1.27, 1.27, 2.54, 2.54],      # [top, bottom, left, right]
        font_family: str = "msyh.ttc",
        font_size  : float = 11,
        font_color : str = "#000000",
        opacity    : str = 1,
        page_range : str = "all",
        unit       : str = "cm",
        output_path: str = None
    ):
    try:
        doc: fitz.Document = fitz.open(doc_path)
        width, height = doc[-1].rect.width, doc[-1].rect.height
        p = Path(doc_path)
        # 生成页眉页脚pdf(相比page.insert_text,此方法生成体积更小)
        hf_output_path = str(p.parent / "tmp_hf.pdf")
        create_header_and_footer_mask(width=width, height=height, content_list=content_list, margin_bbox=margin_bbox,font_family=font_family, font_size=font_size, font_color=font_color, opacity=opacity, unit=unit, output_path=hf_output_path)
        # 插入页眉页脚
        hf_doc = fitz.open(hf_output_path)
        roi_indicies = utils.parse_range(page_range, doc.page_count)
        for page_index in range(doc.page_count):
            page = doc[page_index]
            if page_index in roi_indicies:
                page.show_pdf_page(page.rect, hf_doc, 0, overlay=False)
                page.clean_contents()
        if output_path is None:
            output_path = str(p.parent / f"{p.stem}-加页眉页脚.pdf")
        doc.save(output_path, garbage=3, deflate=True)
        doc.close()
        hf_doc.close()
        os.remove(hf_output_path)
        utils.dump_json(cmd_output_path, {"status": "success", "message": ""})
    except:
        logger.error(traceback.format_exc())
        utils.dump_json(cmd_output_path, {"status": "error", "message": traceback.format_exc()})

@utils.batch_process()
def remove_header_and_footer(doc_path: str,  margin_bbox: List[float], remove_list: List[str] = ['header', 'footer'], unit: str = "cm", page_range: str = "all", output_path: str = None):
    try:
        doc: fitz.Document = fitz.open(doc_path)
        width, height = doc[-1].rect.width, doc[-1].rect.height
        roi_indices = utils.parse_range(page_range, doc.page_count)
        margin_bbox = [utils.convert_length(x, unit, "pt") for x in margin_bbox]
        p = Path(doc_path)
        mask_doc_path = str(p.parent / "tmp_mask.pdf")
        c = canvas.Canvas(mask_doc_path,pagesize=(width, height))
        color = [v/255. for v in utils.hex_to_rgb("#FFFFFF")]
        bbox_list = []
        if "header" in remove_list:
            bbox_list.append([margin_bbox[2], height-margin_bbox[0], width-margin_bbox[2]-margin_bbox[3], margin_bbox[0]]) # left_bottom_x, left_bottom_y, w, h
        if "footer" in remove_list:
            bbox_list.append([margin_bbox[2], 0, width-margin_bbox[2]-margin_bbox[3], margin_bbox[1]])
        for bbox in bbox_list:
            c.setStrokeColorRGB(*color)
            c.setFillColorRGB(*color)
            c.rect(*bbox, fill=True, stroke=False)
        c.showPage()
        c.save()
        mask_doc = fitz.open(mask_doc_path)
        for page_index in range(doc.page_count):
            if page_index in roi_indices:
                page = doc[page_index]
                page.show_pdf_page(page.rect, mask_doc, 0, overlay=True)
                page.clean_contents()
        if output_path is None:
            output_path = str(p.parent / f"{p.stem}-去页眉页脚.pdf")
        doc.save(output_path, garbage=3, deflate=True)
        doc.close()
        mask_doc.close()
        os.remove(mask_doc_path)
        utils.dump_json(cmd_output_path, {"status": "success", "message": ""})
    except:
        logger.error(traceback.format_exc())
        utils.dump_json(cmd_output_path, {"status": "error", "message": traceback.format_exc()})
