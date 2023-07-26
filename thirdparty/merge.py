import glob
import re
import traceback
from pathlib import Path
from typing import List

import fitz
import utils
from constants import cmd_output_path
from loguru import logger


def merge_pdf(doc_path_list: List[str], sort_method: str = "default", sort_direction: str = "asc", output_path: str = None):
    try:
        new_path_list = []
        for doc_path in doc_path_list:
            if "*" in doc_path:
                path_list = glob.glob(doc_path)
                if path_list:
                    new_path_list.extend(path_list)
            else:
                new_path_list.append(doc_path)
        if sort_method == "default":
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
        writer: fitz.Document = fitz.open()
        toc_list = []
        cur_page_number = 0
        for doc_path in new_path_list:
            doc_temp = fitz.open(doc_path)
            toc_temp = doc_temp.get_toc(simple=True)
            if toc_temp:
                toc_temp = list(map(lambda x: [x[0], x[1], x[2]+cur_page_number], toc_temp))
            else:
                toc_temp = [[1, Path(doc_path).stem, cur_page_number+1]]
            toc_list.extend(toc_temp)
            cur_page_number += doc_temp.page_count
            writer.insert_pdf(doc_temp)
        writer.set_toc(toc_list)
        if output_path is None:
            p = Path(doc_path_list[0])
            output_path = str(p.parent / f"{p.stem}(等)合并.pdf").replace("*", "")
        writer.save(output_path, garbage=3, deflate=True)
        utils.dump_json(cmd_output_path, {"status": "success", "message": ""})
    except:
        logger.error(traceback.format_exc())
        utils.dump_json(cmd_output_path, {"status": "error", "message": traceback.format_exc()})
