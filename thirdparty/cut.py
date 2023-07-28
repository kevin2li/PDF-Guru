import glob
import re
import traceback
from pathlib import Path
from typing import List

import fitz
import utils
from constants import cmd_output_path
from loguru import logger

@utils.batch_process()
def cut_pdf_by_grid(doc_path: str, n_row: int, n_col: int, page_range: str = "all", output_path: str = None):
    try:
        doc: fitz.Document = fitz.open(doc_path)
        roi_indices = utils.parse_range(page_range, doc.page_count)
        writer: fitz.Document = fitz.open()
        for page_index in roi_indices:
            page = doc[page_index]
            page_width, page_height = page.rect.width, page.rect.height
            width, height = page_width/n_col, page_height/n_row
            for i in range(n_row):
                for j in range(n_col):
                    bbox = fitz.Rect(j*width, i*height, (j+1)*width, (i+1)*height)
                    # bbox += d
                    tmp_page = writer.new_page(-1, width=bbox.width, height=bbox.height)
                    tmp_page.show_pdf_page(tmp_page.rect, doc, page_index, clip=bbox)
        if output_path is None:
            p = Path(doc_path)
            output_path = str(p.parent / f"{p.stem}-网格分割.pdf")
        writer.save(output_path, garbage=3, deflate=True)
        utils.dump_json(cmd_output_path, {"status": "success", "message": ""})
    except:
        logger.error(traceback.format_exc())
        utils.dump_json(cmd_output_path, {"status": "error", "message": traceback.format_exc()})

@utils.batch_process()
def cut_pdf_by_breakpoints(doc_path: str, h_breakpoints: List[float], v_breakpoints: List[float], page_range: str = "all", output_path: str = None):
    try:
        doc: fitz.Document = fitz.open(doc_path)
        roi_indices = utils.parse_range(page_range, doc.page_count)
        writer: fitz.Document = fitz.open()
        if h_breakpoints:
            h_breakpoints = [v for v in h_breakpoints if 0 <= v <= 1]
            h_breakpoints = [0] + h_breakpoints + [1]
            h_breakpoints.sort()
        else:
            h_breakpoints = [0., 1.]
        if v_breakpoints:
            v_breakpoints = [v for v in v_breakpoints if 0 <= v <= 1]
            v_breakpoints = [0] + v_breakpoints + [1]
            v_breakpoints.sort()
        else:
            v_breakpoints = [0., 1.]
        for page_index in roi_indices:
            page = doc[page_index]
            page_width, page_height = page.rect.width, page.rect.height
            for i in range(len(h_breakpoints)-1):
                for j in range(len(v_breakpoints)-1):
                    bbox = fitz.Rect(v_breakpoints[j]*page_width, h_breakpoints[i]*page_height, v_breakpoints[j+1]*page_width, h_breakpoints[i+1]*page_height)
                    new_page = writer.new_page(-1, width=bbox.width, height=bbox.height)
                    new_page.show_pdf_page(new_page.rect, doc, page_index, clip=bbox)
        if output_path is None:
            p = Path(doc_path)
            output_path = str(p.parent / f"{p.stem}-自定义分割.pdf")
        writer.save(output_path, garbage=3, deflate=True)
        utils.dump_json(cmd_output_path, {"status": "success", "message": ""})
    except:
        logger.error(traceback.format_exc())
        utils.dump_json(cmd_output_path, {"status": "error", "message": traceback.format_exc()})


@utils.batch_process()
def combine_pdf_by_grid(doc_path, n_row: int, n_col: int, paper_size: str = "a4", orientation: str = "portrait", page_range: str = "all", output_path: str = None):
    try:
        doc: fitz.Document = fitz.open(doc_path)
        if paper_size == "same":
            rect = doc[-1].rect
            width, height = rect.width, rect.height
        else:
            if orientation == "landscape":
                paper_size = f"{paper_size}-l"
            width, height = fitz.paper_size(paper_size)
        batch_size = n_row * n_col
        unit_w, unit_h = width / n_col, height / n_row
        r_tab = []
        for i in range(n_row):
            for j in range(n_col):
                rect = fitz.Rect(j*unit_w, i*unit_h, (j+1)*unit_w, (i+1)*unit_h)
                r_tab.append(rect)
        writer: fitz.Document = fitz.open()
        roi_indices = utils.parse_range(page_range, doc.page_count)
        for page_index in roi_indices:
            if page_index % batch_size == 0:
                logger.debug(page_index)
                page = writer.new_page(-1, width=width, height=height)
            page.show_pdf_page(r_tab[page_index % batch_size], doc, page_index)
        if output_path is None:
            p = Path(doc_path)
            output_path = str(p.parent / f"{p.stem}-网格组合.pdf")
        writer.save(output_path, garbage=3, deflate=True)
        utils.dump_json(cmd_output_path, {"status": "success", "message": ""})
    except:
        logger.error(traceback.format_exc())
        utils.dump_json(cmd_output_path, {"status": "error", "message": traceback.format_exc()})
