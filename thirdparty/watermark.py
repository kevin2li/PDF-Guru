import math
import os
import re
import traceback
from pathlib import Path
from typing import List, Tuple, Union

import fitz
import utils
from constants import cmd_output_path
from loguru import logger
from PIL import Image
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.pdfgen import canvas


def create_text_wartmark(
        wm_text              : str,
        width                : Union[int, float],
        height               : Union[int, float],
        font                 : str = "msyh.ttc",
        fontsize             : int = 55,
        angle                : Union[int, float] = 45,
        text_stroke_color_rgb: Tuple[int, int, int] = (0, 1, 0),
        text_fill_color_rgb  : Tuple[int, int, int] = (1, 0, 0),
        text_fill_alpha      : Union[int, float] = 0.3,
        num_lines            : Union[int, float] = 1,
        line_spacing         : Union[int, float] = 2,
        word_spacing         : Union[int, float] = 2,
        x_offset             : Union[int, float] = 0,
        y_offset             : Union[int, float] = 0,
        multiple_mode        : bool = False,
        output_path          : str = None,
    ):
    try:
        if output_path is None:
            output_path = "watermark.pdf"
        c = canvas.Canvas(output_path,pagesize=(width,height))
        pdfmetrics.registerFont(TTFont('custom_font',font))

        parts = wm_text.split("\n")
        max_part = max(parts, key=lambda x: len(x))
        wm_length = c.stringWidth(max_part, "custom_font", fontsize)
        font_length = c.stringWidth("中", "custom_font", fontsize)
        line_height = c.stringWidth(max_part[0], "custom_font", fontsize)*1.1
        wm_height = line_height * len(parts)
        
        c.setFont("custom_font", fontsize)
        c.setStrokeColorRGB(*text_stroke_color_rgb)
        c.setFillColorRGB(*text_fill_color_rgb)
        c.setFillAlpha(text_fill_alpha)
        c.translate(width/2, height/2)
        c.rotate(angle)

        diagonal_length = math.sqrt(width**2 + height**2) # diagonal length of the paper
        if multiple_mode:
            start_y_list = list(map(lambda x: x*wm_height*(line_spacing+1), range(num_lines)))
            center_y = sum(start_y_list) / len(start_y_list)
            start_y_list = list(map(lambda x: x - center_y + y_offset, start_y_list))
            logger.debug(start_y_list)
            for start_y in start_y_list:
                start_x = -diagonal_length + x_offset
                while start_x < diagonal_length:
                    for i, part in enumerate(parts):
                        c.drawString(start_x,start_y-i*line_height,part)
                    start_x += wm_length+font_length*word_spacing
        else:
            start_x = - wm_length/2 + x_offset
            start_y = - wm_height/2 + y_offset
            for i, part in enumerate(parts):
                c.drawString(start_x,start_y-i*line_height,part)
        c.save()
        utils.dump_json(cmd_output_path, {"status": "success", "message": ""})
        return True
    except:
        logger.error(traceback.format_exc())
        utils.dump_json(cmd_output_path, {"status": "error", "message": traceback.format_exc()})
        return False

def create_image_wartmark(
        width        : Union[int, float],
        height       : Union[int, float],
        wm_image_path: str,
        angle        : Union[int, float] = 0,
        scale        : Union[int, float] = 1,
        opacity      : Union[int, float] = 1,
        num_lines    : Union[int, float] = 1,
        word_spacing : Union[int, float] = 0.1,
        line_spacing : Union[int, float] = 2,
        x_offset     : Union[int, float] = 0,
        y_offset     : Union[int, float] = 0,
        multiple_mode: bool = False,
        output_path  : str = None,
    ):
    try:
        if output_path is None:
            output_path = "watermark.pdf"
        c = canvas.Canvas(output_path,pagesize=(width, height))
        diagonal_length = math.sqrt(width**2 + height**2) # diagonal length of the paper
        wm_image = Image.open(wm_image_path)
        wm_width, wm_height = wm_image.size[0]*scale, wm_image.size[1]*scale
        gap = word_spacing*wm_width
        c.translate(width/2, height/2)
        c.setFillAlpha(opacity)
        c.rotate(angle)
        if multiple_mode:
            start_y_list = list(map(lambda x: x*wm_height*(line_spacing+1), range(num_lines)))
            center_y = sum(start_y_list) / len(start_y_list)
            start_y_list = list(map(lambda x: x - center_y + y_offset, start_y_list))
            logger.debug(start_y_list)
            for start_y in start_y_list:
                start_x = -diagonal_length + x_offset
                while start_x < diagonal_length:
                    c.drawImage(wm_image_path, start_x, start_y, width=wm_width, height=wm_height)
                    start_x += wm_width + gap
        else:
            start_x = -wm_width/2 + x_offset
            start_y = -wm_height/2 + y_offset
            c.drawImage(wm_image_path, start_x, start_y, width=wm_width, height=wm_height)
        c.showPage()
        c.save()
        utils.dump_json(cmd_output_path, {"status": "success", "message": ""})
        return True
    except:
        logger.error(traceback.format_exc())
        utils.dump_json(cmd_output_path, {"status": "error", "message": traceback.format_exc()})
        return False

@utils.batch_process()
def watermark_pdf_by_text(doc_path: str, wm_text: str, page_range: str = "all", layer: str = "bottom", output_path: str = None, **args):
    try:
        doc: fitz.Document = fitz.open(doc_path)
        page = doc[-1]
        p = Path(doc_path)
        tmp_wm_path = str(p.parent / "tmp_wm.pdf")
        ok = create_text_wartmark(wm_text=wm_text, width=page.rect.width, height=page.rect.height, output_path=tmp_wm_path, **args)
        if not ok:
            return
        wm_doc: fitz.Document = fitz.open(tmp_wm_path)
        roi_indices = utils.parse_range(page_range, doc.page_count)
        for page_index in range(doc.page_count):
            if page_index in roi_indices:
                page: fitz.Page = doc[page_index]
                overlay = False if layer == "bottom" else True
                page.show_pdf_page(page.rect, wm_doc, 0, overlay=overlay)
                page.clean_contents()
        if output_path is None:
            output_path = p.parent / f"{p.stem}-加水印版.pdf"
        doc.save(output_path, garbage=3, deflate=True)
        wm_doc.close()
        doc.close()
        os.remove(tmp_wm_path)
        utils.dump_json(cmd_output_path, {"status": "success", "message": ""})
    except:
        logger.error(traceback.format_exc())
        utils.dump_json(cmd_output_path, {"status": "error", "message": traceback.format_exc()})

@utils.batch_process()
def watermark_pdf_by_image(doc_path: str, wm_path: str, page_range: str = "all", layer: str = "bottom", output_path: str = None, **args):
    try:
        doc: fitz.Document = fitz.open(doc_path)
        page = doc[-1]
        p = Path(doc_path)
        tmp_wm_path = str(p.parent / "tmp_wm.pdf")
        ok = create_image_wartmark(wm_image_path=wm_path, width=page.rect.width, height=page.rect.height, output_path=tmp_wm_path, **args)
        if not ok:
            return
        wm_doc = fitz.open(tmp_wm_path)
        roi_indices = utils.parse_range(page_range, doc.page_count)
        for i in roi_indices:
            page: fitz.Page = doc[i]
            overlay = False if layer == "bottom" else True
            page.show_pdf_page(page.rect, wm_doc, 0, overlay=overlay)
            page.clean_contents()
        if output_path is None:
            output_path = p.parent / f"{p.stem}-加水印版.pdf"
        doc.save(output_path, garbage=3, deflate=True)
        wm_doc.close()
        doc.close()
        os.remove(tmp_wm_path)
        utils.dump_json(cmd_output_path, {"status": "success", "message": ""})
    except:
        logger.error(traceback.format_exc())
        utils.dump_json(cmd_output_path, {"status": "error", "message": traceback.format_exc()})

@utils.batch_process()
def watermark_pdf_by_pdf(doc_path: str, wm_doc_path: str, page_range: str = "all", layer: str = "bottom", output_path: str = None):
    try:
        doc: fitz.Document = fitz.open(doc_path)
        wm_doc: fitz.Document = fitz.open(wm_doc_path)
        roi_indices = utils.parse_range(page_range, doc.page_count)
        for i in roi_indices:
            page: fitz.Page = doc[i]
            overlay = False if layer == "bottom" else True
            page.show_pdf_page(page.rect, wm_doc, 0, overlay=overlay)
        if output_path is None:
            p = Path(doc_path)
            output_path = p.parent / f"{p.stem}-加水印版.pdf"
        doc.save(output_path, garbage=3, deflate=True)
        wm_doc.close()
        doc.close()
        utils.dump_json(cmd_output_path, {"status": "success", "message": ""})
    except:
        logger.error(traceback.format_exc())
        utils.dump_json(cmd_output_path, {"status": "error", "message": traceback.format_exc()})

@utils.batch_process()
def remove_watermark_by_type(doc_path: str, page_range: str = "all", output_path: str = None):
    try:
        doc: fitz.Document = fitz.open(doc_path)
        roi_indices = utils.parse_range(page_range, doc.page_count)
        WATERMARK_FLAG = False
        for page_index in range(doc.page_count):
            page: fitz.Page = doc[page_index]
            if page_index in roi_indices:
                page.clean_contents()
                xref = page.get_contents()[0]
                stream = doc.xref_stream(xref)
                if stream:
                    stream = bytearray(stream)
                    if stream.find(b"/Subtype/Watermark"):
                        WATERMARK_FLAG = True
                        while True:
                            i1 = stream.find(b"/Artifact")  # start of definition
                            if i1 < 0: break  # none more left: done
                            i2 = stream.find(b"EMC", i1)  # end of definition
                            stream[i1 : i2+3] = b""  # remove the full definition source "/Artifact ... EMC"
                        doc.update_stream(xref, stream, compress=True)
        if not WATERMARK_FLAG:
            logger.error("该文件没有找到水印!")
            utils.dump_json(cmd_output_path, {"status": "error", "message": "该文件没有找到水印!"})
            return
        if output_path is None:
            p = Path(doc_path)
            output_path = str(p.parent / f"{p.stem}-去水印版.pdf")
        doc.save(output_path, garbage=3, deflate=True)
        utils.dump_json(cmd_output_path, {"status": "success", "message": ""})
    except:
        logger.error(traceback.format_exc())
        utils.dump_json(cmd_output_path, {"status": "error", "message": traceback.format_exc()})

@utils.batch_process()
def detect_watermark_index_helper(doc_path: str, wm_page_number: int, outpath: str = None):
    try:
        doc: fitz.Document = fitz.open(doc_path)
        writer: fitz.Document = fitz.open()
        page = doc[wm_page_number]
        keys = doc.xref_get_keys(page.xref)
        logger.debug(keys)
        out = doc.xref_get_key(page.xref, "Contents")
        logger.debug(f"Contents: {out}")
        if out[0] == 'array':
            parts = list(out)[1][1:-1].split(" ")
            indirect_objs = list(map(lambda x: " ".join(x), [parts[i:i+3] for i in range(0, len(parts), 3)]))
            for i in range(len(indirect_objs)):
                t = f'[{" ".join(indirect_objs[:i]+indirect_objs[i+1:])}]'
                doc.xref_set_key(page.xref, "Contents", t)
                writer.insert_pdf(doc, from_page=wm_page_number, to_page=wm_page_number)
        if outpath is None:
            p = Path(doc_path)
            outpath = str(p.parent / f"{p.stem}-识别水印索引.pdf")
        if writer.page_count > 0:
            writer.save(outpath, garbage=3, deflate=True)
        else:
            logger.error("该文件没有找到水印!")
            utils.dump_json(cmd_output_path, {"status": "error", "message": "该文件没有找到水印!"})
            return
        utils.dump_json(cmd_output_path, {"status": "success", "message": ""})
    except:
        logger.error(traceback.format_exc())
        utils.dump_json(cmd_output_path, {"status": "error", "message": traceback.format_exc()})
    
@utils.batch_process()
def remove_watermark_by_index(doc_path: str, wm_index: List[int], page_range: str = "all", output_path: str = None):
    try:
        doc: fitz.Document = fitz.open(doc_path)
        writer: fitz.Document = fitz.open()
        roi_indices = utils.parse_range(page_range, doc.page_count)
        for i in range(len(wm_index)):
            if wm_index[i] < 0:
                wm_index[i] = doc.page_count + wm_index[i]
        wm_index.sort(reverse=True)
        for page_index in range(doc.page_count):
            page = doc[page_index]
            if page_index in roi_indices:
                out = doc.xref_get_key(page.xref, "Contents")
                if out[0] == 'array':
                    parts = list(out)[1][1:-1].split(" ")
                    indirect_objs = list(map(lambda x: " ".join(x), [parts[i:i+3] for i in range(0, len(parts), 3)]))
                    for i in wm_index:
                        del indirect_objs[i]                    
                    filtered_objs = f'[{" ".join(indirect_objs)}]'
                    doc.xref_set_key(page.xref, "Contents", filtered_objs)
            writer.insert_pdf(doc, from_page=page_index, to_page=page_index)
        if output_path is None:
            p = Path(doc_path)
            output_path = str(p.parent / f"{p.stem}-去水印版.pdf")
        writer.save(output_path, garbage=3, deflate=True)
        utils.dump_json(cmd_output_path, {"status": "success", "message": ""})
    except:
        logger.error(traceback.format_exc())
        utils.dump_json(cmd_output_path, {"status": "error", "message": traceback.format_exc()})

# 根据字节流去水印
@utils.batch_process()
def remove_watermark_by_text(doc_path: str, wm_text: str, output_path: str = None):
    try:
        import pdf_redactor
        options = pdf_redactor.RedactorOptions()
        options.content_filters = [
            # First convert all dash-like characters to dashes.
            (
                re.compile(wm_text),
                lambda m : ""
            ),
        ]
        if output_path is None:
            p = Path(doc_path)
            output_path = str(p.parent / f"{p.stem}-去水印版.pdf")
        options.input_stream = doc_path
        options.output_stream = output_path
        pdf_redactor.redactor(options)
        utils.dump_json(cmd_output_path, {"status": "success", "message": ""})
    except:
        logger.error(traceback.format_exc())
        utils.dump_json(cmd_output_path, {"status": "error", "message": traceback.format_exc()})