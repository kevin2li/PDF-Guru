import glob
import re
import traceback
from pathlib import Path
from typing import List

import fitz
import utils
from constants import cmd_output_path
from loguru import logger
import os
from header_and_footer import remove_header_and_footer, create_header_and_footer_mask

@utils.batch_process()
def insert_page_number(
        doc_path   : str,
        format     : str,
        pos        : str        = "footer",
        start      : int         = 0,
        margin_bbox: List[float] = [1.27, 1.27, 2.54, 2.54],
        font_family: str         = "msyh.ttc",
        font_size  : float      = 11,
        font_color : str        = "#000000",
        opacity    : str        = 1,
        align      : str        = "center",
        page_range : str        = "all",
        unit       : str        = "cm",
        output_path: str         = None
    ):
    """ 页码样式
    {
        "0":"1,2,3...",
        "1":"1/X",
        "2":"第1页",
        "3":"第1/X页",
        "4":"第1页，共X页",
        "5":"-1-,-2-,-3-...",
        "6":"第一页",
        "7":"第一页，共X页",
        "8":"I,II,III...",
        "9":"i,ii,iii...",
        "10":"A,B,C...",
        "11":"a,b,c...",
    }
    """
    try:
        doc: fitz.Document = fitz.open(doc_path)
        roi_indices = utils.parse_range(page_range, doc.page_count)
        pno = start
        for page_index in range(doc.page_count):
            page = doc[page_index]
            if page_index in roi_indices:
                if format == "0":
                    content = f"{pno}"
                elif format == "1":
                    content = f"{pno}/{doc.page_count}"
                elif format == "2":
                    content = f"第{pno}页"
                elif format == "3":
                    content = f"第{pno}/{doc.page_count}页"
                elif format == "4":
                    content = f"第{pno}页，共{doc.page_count}页"
                elif format == "5":
                    content = f"-{pno}-"
                elif format == "6":
                    content = f"第{utils.num_to_chinese(pno)}页"
                elif format == "7":
                    content = f"第{utils.num_to_chinese(pno)}页，共{utils.num_to_chinese(doc.page_count)}页"
                elif format == "8":
                    content = f"{utils.num_to_roman(pno)}"
                elif format == "9":
                    content = f"{utils.num_to_roman(pno).lower()}"
                elif format == "10":
                    content = f"{utils.num_to_letter(pno)}"
                elif format == "11":
                    content = f"{utils.num_to_letter(pno).lower()}"
                else:
                    content = format.replace("%p", str(pno)).replace("%P", str(doc.page_count))
                pno += 1
                hf_output_path = str(Path(doc_path).parent / f"tmp_hf.pdf")
                content_list = [""]*6
                if pos == "header":
                    if align == "left":
                        content_list[0] = content
                    elif align == "center":
                        content_list[1] = content
                    elif align == "right":
                        content_list[2] = content
                else:
                    if align == "left":
                        content_list[3] = content
                    elif align == "center":
                        content_list[4] = content
                    elif align == "right":
                        content_list[5] = content
                create_header_and_footer_mask(width=page.rect.width, height=page.rect.height, content_list=content_list, margin_bbox=margin_bbox,font_family=font_family, font_size=font_size, font_color=font_color, opacity=opacity, unit=unit, output_path=hf_output_path)
                hf_doc: fitz.Document = fitz.open(hf_output_path)
                page.show_pdf_page(page.rect, hf_doc, 0, overlay=True)
        if output_path is None:
            p = Path(doc_path)
            output_path = str(p.parent / f"{p.stem}-加页码.pdf")
        doc.save(output_path, garbage=3, deflate=True)
        hf_doc.close()
        doc.close()
        os.remove(hf_output_path)
        utils.dump_json(cmd_output_path, {"status": "success", "message": ""})
    except:
        logger.error(traceback.format_exc())
        utils.dump_json(cmd_output_path, {"status": "error", "message": traceback.format_exc()})


@utils.batch_process()
def remove_page_number(doc_path: str, margin_bbox: List[float], pos: str = "footer", unit: str = "cm", page_range: str = "all", output_path: str = None):
    try:
        remove_header_and_footer(doc_path=doc_path, margin_bbox=margin_bbox, remove_list=[pos], unit=unit, page_range=page_range, output_path=output_path)
        utils.dump_json(cmd_output_path, {"status": "success", "message": ""})
    except:
        logger.error(traceback.format_exc())
        utils.dump_json(cmd_output_path, {"status": "error", "message": traceback.format_exc()})
