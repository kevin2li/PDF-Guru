import json
import shutil
import subprocess
import traceback
from pathlib import Path

import fitz
import utils
from constants import cmd_output_path
from loguru import logger

def make_dual_layer_pdf(input_path: str, page_range: str = 'all', lang: str = 'chi_sim', dpi: int = 300, output_path: str = None):
    try:
        tesseract_path = None
        with open("config.json", "r") as f:
            config = json.load(f)
            if not config['tesseract_path']:
                utils.dump_json(cmd_output_path, {"status": "error", "message": "请先配置tesseract路径"})
                return
            tesseract_path = config['tesseract_path']

        # tesseract_path = "C:\\Program Files\\Tesseract-OCR\\tesseract.exe"
        doc: fitz.Document = fitz.open(input_path)
        writer: fitz.Document = fitz.open()
        roi_indices = utils.parse_range(page_range, doc.page_count)
        toc = doc.get_toc(simple=True)

        p = Path(input_path)
        temp_dir = p.parent / "temp"
        temp_dir.mkdir(exist_ok=True, parents=True)

        for page_index in range(doc.page_count):
            page = doc[page_index]
            if page_index in roi_indices:
                pix = page.get_pixmap(matrix=fitz.Matrix(dpi/72, dpi/72))
                img_save_path = str(temp_dir / f"{page_index}.png")
                pix.pil_save(img_save_path, dpi=(dpi, dpi))
                pdf_save_path = str(temp_dir / f"{page_index}")
                result = subprocess.run([tesseract_path, img_save_path, pdf_save_path, "-l", lang, "pdf"], capture_output=True, text=True, creationflags=subprocess.CREATE_NO_WINDOW)
                if result.returncode != 0:
                    logger.error(result)
                    utils.dump_json(cmd_output_path, {"status": "error", "message": str(result)})
                    return
                else:
                    new_page = writer.new_page(width=page.rect.width, height=page.rect.height)
                    pdf = fitz.open(f"{pdf_save_path}.pdf")
                    new_page.show_pdf_page(page.rect, pdf, 0)
                    pdf.close()
            else:
                writer.insert_pdf(doc, from_page=page_index, to_page=page_index)

        writer.set_toc(toc)
        if output_path is None:
            output_path = p.parent / f"{p.stem}-双层.pdf"
        writer.ez_save(output_path)
        writer.close()
        doc.close()
        shutil.rmtree(temp_dir)
        utils.dump_json(cmd_output_path, {"status": "success", "message": ""})
    except:
        logger.error(traceback.format_exc())
        utils.dump_json(cmd_output_path, {"status": "error", "message": traceback.format_exc()})


@utils.batch_process()
def make_dual_layer_pdf_from_image(doc_path: str, lang: str = 'chi_sim',  output_path: str = None):
    try:
        tesseract_path = None
        with open("config.json", "r") as f:
            config = json.load(f)
            if not config['tesseract_path']:
                utils.dump_json(cmd_output_path, {"status": "error", "message": "请先配置tesseract路径"})
                return
            tesseract_path = config['tesseract_path']
        if output_path is None:
            p = Path(doc_path)
            output_path = p.parent / f"{p.stem}-双层"
        result = subprocess.run([tesseract_path, doc_path, output_path, "-l", lang, "pdf"], capture_output=True, text=True, creationflags=subprocess.CREATE_NO_WINDOW)
        if result.returncode != 0:
            logger.error(result)
            utils.dump_json(cmd_output_path, {"status": "error", "message": str(result)})
            return
    except:
        logger.error(traceback.format_exc())
        utils.dump_json(cmd_output_path, {"status": "error", "message": traceback.format_exc()})
