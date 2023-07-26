import glob
import re
import traceback
from pathlib import Path
from typing import List, Union

import fitz
import utils
from constants import cmd_output_path
from loguru import logger

def convert_to_image_pdf(doc_path: Union[str, List[str]], dpi: int = 300, page_range: str = "all", output_path: str = None):
    try:
        path_list = []
        if isinstance(doc_path, str):
            if "*" in doc_path:
                path_list = glob.glob(doc_path)
            else:
                path_list = [doc_path]
        elif isinstance(doc_path, list):
            for p in doc_path:
                if "*" in p:
                    path_list.extend(glob.glob(p))
                else:
                    path_list.append(p)
        for path in path_list:
            doc: fitz.Document = fitz.open(path)
            writer: fitz.Document = fitz.open()
            roi_indices = utils.parse_range(page_range, doc.page_count)
            toc = doc.get_toc(simple=True)
            logger.debug(toc)
            for page_index in range(doc.page_count):
                page = doc[page_index]
                new_page = writer.new_page(width=page.rect.width, height=page.rect.height)
                if page_index in roi_indices:
                    pix = page.get_pixmap(matrix=fitz.Matrix(dpi/72, dpi/72))
                    pix.set_dpi(dpi, dpi)
                    new_page.insert_image(new_page.rect, pixmap=pix)
                else:
                    writer.insert_pdf(doc, from_page=page_index, to_page=page_index)
            if output_path is None:
                p = Path(path)
                output_path = str(p.parent / f"{p.stem}-图片型.pdf")
            writer.set_toc(toc)
            writer.ez_save(output_path)
        utils.dump_json(cmd_output_path, {"status": "success", "message": ""})
    except:
        logger.error(traceback.format_exc())
        utils.dump_json(cmd_output_path, {"status": "error", "message": traceback.format_exc()})

def convert_pdf2png(doc_path: str, dpi: int = 300, page_range: str = "all", output_path: str = None):
    try:
        path_list = []
        if isinstance(doc_path, str):
            if "*" in doc_path:
                path_list = glob.glob(doc_path)
            else:
                path_list = [doc_path]
        elif isinstance(doc_path, list):
            for p in doc_path:
                if "*" in p:
                    path_list.extend(glob.glob(p))
                else:
                    path_list.append(p)
        for path in path_list:
            doc: fitz.Document = fitz.open(path)
            roi_indices = utils.parse_range(page_range, doc.page_count)
            p = Path(path)
            if output_path is None:
                output_dir = p.parent / f"{p.stem}-png"
                output_dir.mkdir(exist_ok=True, parents=True)
            else:
                output_dir = Path(output_path)
                output_dir.mkdir(exist_ok=True, parents=True)
            for i in roi_indices:
                page = doc[i]
                pix = page.get_pixmap(matrix=fitz.Matrix(dpi/72, dpi/72))
                pix.set_dpi(dpi, dpi)
                pix.save(str(output_dir / f"{p.stem}-page-{i+1}.png"))
            utils.dump_json(cmd_output_path, {"status": "success", "message": ""})
    except:
        logger.error(traceback.format_exc())
        utils.dump_json(cmd_output_path, {"status": "error", "message": traceback.format_exc()})

def convert_pdf2svg(doc_path: str, dpi: int = 300, page_range: str = "all", output_path: str = None):
    try:
        path_list = []
        if isinstance(doc_path, str):
            if "*" in doc_path:
                path_list = glob.glob(doc_path)
            else:
                path_list = [doc_path]
        elif isinstance(doc_path, list):
            for p in doc_path:
                if "*" in p:
                    path_list.extend(glob.glob(p))
                else:
                    path_list.append(p)
        for path in path_list:
            doc: fitz.Document = fitz.open(path)
            roi_indices = utils.parse_range(page_range, doc.page_count)
            p = Path(path)
            if output_path is None:
                output_dir = p.parent / f"{p.stem}-svg"
                output_dir.mkdir(exist_ok=True, parents=True)
            else:
                output_dir = Path(output_path)
                output_dir.mkdir(exist_ok=True, parents=True)
            for i in roi_indices:
                page = doc[i]
                out = page.get_svg_image(matrix=fitz.Matrix(dpi/72, dpi/72))
                with open(str(output_dir / f"{p.stem}-page-{i+1}.svg"), "w") as f:
                    f.write(out)
            utils.dump_json(cmd_output_path, {"status": "success", "message": ""})
    except:
        logger.error(traceback.format_exc())
        utils.dump_json(cmd_output_path, {"status": "error", "message": traceback.format_exc()})

def convert_svg2pdf(
        input_path: Union[str, List[str]],
        is_merge: bool = True,
        sort_method: str = 'name',
        sort_direction: str = 'asc',
        paper_size: str = "a4",
        orientation: str = "portrait",
        output_path: str = None):
    try:
        path_list = []
        if isinstance(input_path, str):
            if "*" in input_path:
                path_list = glob.glob(input_path)
            else:
                path_list = [input_path]
        elif isinstance(input_path, list):
            for p in input_path:
                if "*" in p:
                    path_list.extend(glob.glob(p))
                else:
                    path_list.append(p)
        
        if is_merge:
            if output_path is None:
                p = Path(path_list[0])
                output_path = str(p.parent / f"{p.stem}(等)-合并.pdf")
            writer: fitz.Document = fitz.open()
            new_path_list = path_list
            if sort_method == "custom":
                if sort_direction == "asc":
                    pass
                else:
                    new_path_list = new_path_list[::-1]
            elif sort_method == "name":
                if sort_direction == "asc":
                    new_path_list.sort()
                else:
                    new_path_list.sort(reverse=True)
            elif sort_method == "name_digit":
                new_path_list = sorted(new_path_list, key=lambda x: int(re.search(r"\d+$", Path(x).stem).group()))
                if sort_direction == "asc":
                    pass
                else:
                    new_path_list = new_path_list[::-1]
            # create time
            elif sort_method == "ctime":
                if sort_direction == "asc":
                    new_path_list.sort(key=lambda x: Path(x).stat().st_ctime)
                else:
                    new_path_list.sort(key=lambda x: Path(x).stat().st_ctime, reverse=True)
            # modify time
            elif sort_method == "mtime":
                if sort_direction == "asc":
                    new_path_list.sort(key=lambda x: Path(x).stat().st_mtime)
                else:
                    new_path_list.sort(key=lambda x: Path(x).stat().st_mtime, reverse=True)

            for path in new_path_list:
                with open(path, 'r') as f:
                    img = fitz.open(path)
                    if paper_size == "same":
                        w, h = img[0].rect.width, img[0].rect.height
                    else:
                        fmt = fitz.paper_rect(f"{paper_size}-l") if orientation == "landscape" else fitz.paper_rect(paper_size)
                        w, h = fmt.width, fmt.height
                    pdfbytes = img.convert_to_pdf()
                    pdf = fitz.open('pdf', pdfbytes)
                    page = writer.new_page(width=w, height=h)
                    page.show_pdf_page(img[0].rect, pdf, 0)

            writer.save(output_path, garbage=3, deflate=True)
        else:
            if output_path is None:
                p = Path(path_list[0])
                output_dir = p.parent
            else:
                output_dir = Path(output_path)
                output_dir.mkdir(exist_ok=True, parents=True)
            for path in path_list:
                img = fitz.open(path)
                pdfbytes = img.convert_to_pdf()
                pdf = fitz.open('pdf', pdfbytes) 
                savepath = str(output_dir / f"{Path(path).stem}.pdf")
                pdf.save(savepath, garbage=3, deflate=True)
        utils.dump_json(cmd_output_path, {"status": "success", "message": ""})
    except:
        logger.error(traceback.format_exc())
        utils.dump_json(cmd_output_path, {"status": "error", "message": traceback.format_exc()})

def convert_png2pdf(**kwargs):
    convert_svg2pdf(**kwargs)

def convert_anydoc2pdf(input_path: str, output_path: str = None):
    """
    supported document types: PDF, XPS, EPUB, MOBI, FB2, CBZ, SVG
    """
    try:
        path_list = []
        if isinstance(input_path, str):
            if "*" in input_path:
                path_list = glob.glob(input_path)
            else:
                path_list = [input_path]
        elif isinstance(input_path, list):
            for p in input_path:
                if "*" in p:
                    path_list.extend(glob.glob(p))
                else:
                    path_list.append(p)
        for path in path_list:
            doc = fitz.open(path)
            b = doc.convert_to_pdf()  # convert to pdf
            pdf = fitz.open("pdf", b)  # open as pdf

            toc= doc.get_toc()  # table of contents of input
            pdf.set_toc(toc)  # simply set it for output
            meta = doc.metadata  # read and set metadata
            if not meta["producer"]:
                meta["producer"] = "PyMuPDF" + fitz.VersionBind

            if not meta["creator"]:
                meta["creator"] = "PyMuPDF PDF converter"
            meta["modDate"] = fitz.get_pdf_now()
            meta["creationDate"] = meta["modDate"]
            pdf.set_metadata(meta)

            # now process the links
            link_cnti = 0
            link_skip = 0
            for pinput in doc:  # iterate through input pages
                links = pinput.get_links()  # get list of links
                link_cnti += len(links)  # count how many
                pout = pdf[pinput.number]  # read corresp. output page
                for l in links:  # iterate though the links
                    if l["kind"] == fitz.LINK_NAMED:  # we do not handle named links
                        logger.info("named link page", pinput.number, l)
                        link_skip += 1  # count them
                        continue
                    pout.insert_link(l)  # simply output the others

            # save the conversion result
            if output_path is None:
                p = Path(path)
                output_path = str(p.parent / f"{p.stem}.pdf")
            pdf.save(output_path, garbage=4, deflate=True)
        utils.dump_json(cmd_output_path, {"status": "success", "message": ""})
    except:
        logger.error(traceback.format_exc())
        utils.dump_json(cmd_output_path, {"status": "error", "message": traceback.format_exc()})
