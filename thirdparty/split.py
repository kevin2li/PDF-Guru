import traceback
from pathlib import Path

import fitz
import utils
from constants import cmd_output_path
from loguru import logger


@utils.batch_process()
def split_pdf_by_chunk(doc_path: str, chunk_size: int, output_path: str = None):
    try:
        doc: fitz.Document = fitz.open(doc_path)
        p = Path(doc_path)
        if output_path is None:
            output_dir = p.parent / "PDF拆分-分块"
            output_dir.mkdir(parents=True, exist_ok=True)
        else:
            output_dir = Path(output_path)
            output_dir.mkdir(parents=True, exist_ok=True)
        for i in range(0, doc.page_count, chunk_size):
            savepath = str(output_dir / f"{p.stem}-{i+1}-{min(i+chunk_size, doc.page_count)}.pdf")
            writer:fitz.Document = fitz.open()
            writer.insert_pdf(doc, from_page=i, to_page=min(i+chunk_size, doc.page_count)-1)
            writer.save(savepath, garbage=3, deflate=True)
        utils.dump_json(cmd_output_path, {"status": "success", "message": ""})
    except:
        logger.error(traceback.format_exc())
        utils.dump_json(cmd_output_path, {"status": "error", "message": traceback.format_exc()})

@utils.batch_process()
def split_pdf_by_page(doc_path: str, page_range: str = "all", output_path: str = None):
    try:
        doc: fitz.Document = fitz.open(doc_path)
        p = Path(doc_path)
        indices_list = utils.parse_range(page_range, doc.page_count, is_multi_range=True)
        if output_path is None:
            output_dir = p.parent / "PDF拆分-自定义范围"
            output_dir.mkdir(parents=True, exist_ok=True)
        else:
            output_dir = Path(output_path)
            output_dir.mkdir(parents=True, exist_ok=True)
        for i, indices in enumerate(indices_list):
            writer: fitz.Document = fitz.open()
            parts = utils.range_compress(indices)
            for part in parts:
                writer.insert_pdf(doc, from_page=part[0], to_page=part[1])
            writer.save(str(output_dir / f"{p.stem}-part{i}.pdf"), garbage=3, deflate=True)
        utils.dump_json(cmd_output_path, {"status": "success", "message": ""})
    except:
        logger.error(traceback.format_exc())
        utils.dump_json(cmd_output_path, {"status": "error", "message": traceback.format_exc()})

@utils.batch_process()
def split_pdf_by_toc(doc_path: str, level: int = 1, output_path: str = None):
    try:
        doc: fitz.Document = fitz.open(doc_path)
        p = Path(doc_path)
        toc = doc.get_toc(simple=True)
        if output_path is None:
            output_dir = p.parent / "PDF拆分-目录"
            output_dir.mkdir(parents=True, exist_ok=True)
        else:
            output_dir = Path(output_path)
            output_dir.mkdir(parents=True, exist_ok=True)
        roi_toc = [[i, p] for i, p in enumerate(toc) if p[0] == level]
        begin, end = 0, 0
        for i, p in enumerate(roi_toc):
            # p: [index, [level, title, page_index]
            begin, end = None, None
            cur_idx, next_idx = 0, 0
            if i < len(roi_toc)-1:
                begin = p[1][-1]-1
                end = roi_toc[i+1][1][-1]-2
                cur_idx = p[0]
                next_idx = roi_toc[i+1][0]
            else:
                begin = p[1][-1]-1
                end = doc.page_count-1
                cur_idx = p[0]
                next_idx = len(toc)
            writer: fitz.Document = fitz.open()
            writer.insert_pdf(doc, from_page=begin, to_page=end)
            title = p[1][1].replace("/", "-").replace("\\", "-").replace(":", "-").replace("?","-").replace("*", "-").replace("\"", "-").replace("<", "-").replace(">", "-").replace("|", "-")

            tmp_toc = list(map(lambda x: [x[0], x[1], x[2]-begin],toc[cur_idx:next_idx]))
            writer.set_toc(tmp_toc)
            writer.save(str(output_dir / f"{title}.pdf"), garbage=3, deflate=True)
        utils.dump_json(cmd_output_path, {"status": "success", "message": ""})
    except:
        logger.error(traceback.format_exc())
        utils.dump_json(cmd_output_path, {"status": "error", "message": traceback.format_exc()})
