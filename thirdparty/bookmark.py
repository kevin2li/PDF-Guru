import json
import re
import traceback
from pathlib import Path
from typing import List

import fitz
import utils
from constants import cmd_output_path
from loguru import logger


def title_preprocess(title: str, rules: List[dict] = None):
    """提取标题层级和标题内容
    """
    try:
        title = title.rstrip()
        res = {}
        # 优先根据rule匹配
        if rules:
            for rule in rules:
                if rule['type'] != "custom":
                    if rule['prefix'] in ["1", "1."]:
                        m = re.match("\s*(\d+\.?)\s+(.+)", title)
                        if m is not None:
                            res['text'] = f"{m.group(1)} {m.group(2)}"
                            res['level'] = int(rule["level"])
                            return res
                    elif rule["prefix"] == "1.1":
                        m = re.match("\s*(\d+\.\d+\.?)\s+(.+)", title)
                        if m is not None:
                            res['text'] = f"{m.group(1)} {m.group(2)}"
                            res['level'] = int(rule["level"])
                            return res
                    elif rule["prefix"] == "1.1.1":
                        m = re.match("\s*(\d+\.\d+\.\d+\.?)\s+(.+)", title)
                        if m is not None:
                            res['text'] = f"{m.group(1)} {m.group(2)}"
                            res['level'] = int(rule["level"])
                            return res
                    elif rule["prefix"] == "1.1.1.1":
                        m = re.match("\s*(\d+\.\d+\.\d+\.\d+\.?)\s+(.+)", title)
                        if m is not None:
                            res['text'] = f"{m.group(1)} {m.group(2)}"
                            res['level'] = int(rule["level"])
                            return res
                    elif rule["prefix"] in ["第一章", "第一节", "第一小节", "第一卷", "第一编", "第一部分", "第一课"]:
                        m = re.match("\s*(第.+[章|节|编|卷|部分|课])\s*(.+)", title)
                        if m is not None:
                            res['text'] = f"{m.group(1)} {m.group(2)}"
                            res['level'] = int(rule["level"])
                            return res
                    elif rule["prefix"] in ["Chapter 1", "Lesson 1"]:
                        m = re.match("\s*((Chapter|Lesson) \d+\.?)\s*(.+)", title)
                        if m is not None:
                            res['text'] = f"{m.group(1)} {m.group(2)}"
                            res['level'] = int(rule["level"])
                            return res
                    elif rule["prefix"] in ["一、", "一."]:
                        m = re.match("\s*([一二三四五六七八九十]+[、.])\s*(.+)", title)
                        if m is not None:
                            res['text'] = f"{m.group(1)} {m.group(2)}"
                            res['level'] = int(rule["level"])
                            return res
                else:
                    m = re.match(f'\s*({rule["prefix"]})\s+(.+)', title)
                    if m is not None:
                        res['text'] = f"{m.group(1)} {m.group(2)}"
                        res['level'] = int(rule["level"])
                        return res
        # 其次根据缩进匹配
        if title.startswith("\t"):
            m = re.match("(\t*)\s*(.+)", title)
            res['text'] = f"{m.group(2)}".rstrip()
            res['level'] = len(m.group(1))+1
            return res
        
        # 无匹配
        res['text'] = title
        res['level'] = 1
        return res
    except:
        return {'level': 1, "text": title}

@utils.batch_process()
def add_toc_from_file(toc_path: str, doc_path: str, offset: int, output_path: str = None):
    """从目录文件中导入书签到pdf文件(若文件中存在行没指定页码则按1算)

    Args:
        toc_path (str): 目录文件路径
        doc_path (str): pdf文件路径
        offset (int): 偏移量, 计算方式: “pdf文件实际页码” - “目录文件标注页码”
    """
    try:
        doc: fitz.Document = fitz.open(doc_path)
        p = Path(doc_path)
        toc_path = Path(toc_path)
        toc = []
        if toc_path.suffix == ".txt":
            with open(toc_path, "r", encoding="utf-8") as f:
                for line in f:
                    pno = 1
                    title = line
                    m = re.search("(\d+)(?=\s*$)", line) # 把最右侧的数字当作页码，如果解析的数字超过pdf总页数，就从左边依次删直到小于pdf总页数为止
                    if m is not None:
                        pno = int(m.group(1))
                        while pno > doc.page_count:
                            pno = int(str(pno)[1:])
                        title = line[:m.span()[0]]
                    pno = pno + offset
                    if not title.strip(): # 标题为空跳过
                        continue
                    res = title_preprocess(title)  
                    level, title = res['level'], res['text']
                    # 参考：https://pymupdf.readthedocs.io/en/latest/document.html#Document.get_toc
                    toc.append([level, title, pno, {"kind":1, "zoom":1, "to": fitz.Point(0, 0)}]) # [level, title, page [, dest]]
        elif toc_path.suffix == ".json":
            with open(toc_path, "r", encoding="utf-8") as f:
                toc = json.load(f)
        else:
            logger.error("不支持的toc文件格式!")
            utils.dump_json(cmd_output_path, "不支持的toc文件格式!")
            return
        # 校正层级
        levels = [v[0] for v in toc]
        diff = [levels[i+1]-levels[i] for i in range(len(levels)-1)]
        indices = [i for i in range(len(diff)) if diff[i] > 1]
        for idx in indices:
            toc[idx][0] = toc[idx+1][0]
        logger.debug(toc)
        doc.set_toc(toc)
        if output_path is None:
            output_path = str(p.parent / f"{p.stem}-加书签目录.pdf")
        if output_path != doc_path:
            doc.save(output_path, garbage=3, deflate=True)
        else:
            doc.save(doc_path, deflate=True, incremental=True)
        utils.dump_json(cmd_output_path, {"status": "success", "message": ""})
    except:
        logger.error(traceback.format_exc())
        utils.dump_json(cmd_output_path, {"status": "error", "message": traceback.format_exc()})

@utils.batch_process()
def add_toc_by_gap(doc_path: str, gap: int = 1, format: str = "第%p页", start_number: int = 1, page_range: str = "all", output_path: str = None):
    try:
        doc: fitz.Document = fitz.open(doc_path)
        p = Path(doc_path)
        toc = []
        roi_indicies = utils.parse_range(page_range, doc.page_count)
        n = len(roi_indicies)
        for i in range(0, n, gap):
            toc.append([1, format.replace("%p", str(start_number)), roi_indicies[i]+1])
            start_number += gap
        # toc.append([1, format.replace("%p", str(doc.page_count)), doc.page_count])
        doc.set_toc(toc)
        if output_path is None:
            output_path = str(p.parent / f"{p.stem}-[页码书签版].pdf")
        doc.save(output_path, garbage=3, deflate=True)
        utils.dump_json(cmd_output_path, {"status": "success", "message": ""})
    except:
        logger.error(traceback.format_exc())
        utils.dump_json(cmd_output_path, {"status": "error", "message": traceback.format_exc()})

@utils.batch_process()
def extract_toc(doc_path: str, format: str = "txt", output_path: str = None):
    try:
        doc: fitz.Document = fitz.open(doc_path)
        p = Path(doc_path)
        toc = doc.get_toc(simple=False)
        if not toc:
            utils.dump_json(cmd_output_path, {"status": "error", "message": "该文件没有书签!"})
            return
        if format == "txt":
            if output_path is None:
                output_path = str(p.parent / f"{p.stem}-书签.txt")
            with open(output_path, "w", encoding="utf-8") as f:
                for line in toc:
                    indent = (line[0]-1)*"\t"
                    f.writelines(f"{indent}{line[1]} {line[2]}\n")
        elif format == "json":
            if output_path is None:
                output_path = str(p.parent / f"{p.stem}-书签.json")
            for i in range(len(toc)):
                try:
                    toc[i][-1] = toc[i][-1]['to'].y
                except:
                    toc[i][-1] = 0
            with open(output_path, "w", encoding="utf-8") as f:
                json.dump(toc, f)
        utils.dump_json(cmd_output_path, {"status": "success", "message": ""})
    except:
        logger.error(traceback.format_exc())
        utils.dump_json(cmd_output_path, {"status": "error", "message": traceback.format_exc()})

def transform_toc_file(toc_path: str, level_dict_list: List[dict] = None, add_offset: int = 0, delete_level_below: int = None, default_level: int = 1, is_remove_blanklines: bool = True, output_path: str = None):
    try:
        logger.debug(level_dict_list)
        if output_path is None:
            p = Path(toc_path)
            output_path = str(p.parent / f"{p.stem}-书签转换.txt")
        with open(toc_path, "r", encoding="utf-8") as f, open(output_path, "w", encoding="utf-8") as f2:
            for line in f:
                if not line.strip(): # 空行
                    if is_remove_blanklines:
                        continue
                    else:
                        f2.write(f"{line}\n")
                        continue
                old_line = line
                new_line = line
                if add_offset:
                    m = re.search("(\d+)(?=\s*$)", new_line)
                    if m is not None:
                        pno = int(m.group(1))
                        pno = pno + add_offset
                        new_line = new_line[:m.span()[0]-1] + f" {pno}\n"
                        old_line = new_line # 页码更新不算
                if level_dict_list:
                    out = title_preprocess(new_line, level_dict_list)
                    new_line = "\t"*(out['level']-1) + out['text'] + "\n"
                if delete_level_below:
                    if new_line.startswith("\t"*(delete_level_below-1)):
                        continue
                if new_line == old_line: # 没有发生变化
                    new_line = "\t"*(default_level-1) + old_line
                f2.write(new_line)
            f2.flush()
        utils.dump_json(cmd_output_path, {"status": "success", "message": ""})
    except:
        logger.error(traceback.format_exc())
        utils.dump_json(cmd_output_path, {"status": "error", "message": traceback.format_exc()})

def flags_decomposer(flags):
    """Make font flags human readable."""
    l = []
    if flags & 2 ** 0:
        l.append("superscript")
    if flags & 2 ** 1:
        l.append("italic")
    if flags & 2 ** 2:
        l.append("serifed")
    else:
        l.append("sans")
    if flags & 2 ** 3:
        l.append("monospaced")
    else:
        l.append("proportional")
    if flags & 2 ** 4:
        l.append("bold")
    return ", ".join(l)

# 根据字体属性生成目录
def find_title_by_rect_annot(doc_path: str, page_range: str = "all", output_path: str = None):
    try:
        doc: fitz.Document = fitz.open(doc_path)
        toc_examples = []
        for page_index in range(doc.page_count):
            page = doc[page_index]
            for annot in page.annots():
                if annot.type[0] == 4: # Square
                    level = int(annot.info['content']) if annot.info['content'] else 1
                    toc_examples.append({'level': level, 'page': page_index, 'rect': annot.rect})
                    page.delete_annot(annot)
        if not toc_examples:
            logger.error("没有发现矩形注释！")
            utils.dump_json(cmd_output_path, {"status": "error", "message": "没有发现矩形注释！"})
            return

        level_styles = {}
        for i, item in enumerate(toc_examples):
            page = doc[item['page']]
            blocks = page.get_text("dict", flags=11)['blocks']
            words = page.get_text("words") # (x0, y0, x1, y1, "string", blocknumber, linenumber, wordnumber)
            rect = item['rect']
            roi_words = {
                "words": [],
                "properties": [],
            }
            for word in words:
                *word_rect, text, blocknumber, linenumber, wordnumber = word
                if utils.contains_rect(rect, word_rect):
                    roi_words['words'].append(text)
                    lines = blocks[blocknumber]['lines'][linenumber]
                    for span in lines['spans']:
                        if utils.contains_rect(span['bbox'], word_rect):
                            properties = {
                                "size": span['size'],
                                'font': span['font'],
                                'color': span['color'],
                                'flags': span['flags'],
                                'ascender': span['ascender'],
                                'descender': span['ascender'],
                            }
                            properties_str = json.dumps(properties)
                            roi_words['properties'].append(properties_str)
                            break
            if item['level'] not in level_styles:
                level_styles[item['level']] = roi_words['properties']
            else:
                level_styles[item['level']].extend(roi_words['properties'])
        # remove duplicate styles
        for level, styles in level_styles.items():
            level_styles[level] = list(set(styles))

        logger.debug(level_styles)

        toc = []
        roi_indicies = utils.parse_range(page_range, doc.page_count)
        for page_index in roi_indicies:
            page = doc[page_index]
            words = page.get_text("words") # (x0, y0, x1, y1, "string", blocknumber, linenumber, wordnumber)
            blocks = page.get_text("dict", flags=11)['blocks']
            temp = ""
            last_level = -1
            last_block = -1
            for word in words:
                *word_rect, text, blocknumber, linenumber, wordnumber = word
                lines = blocks[blocknumber]['lines'][linenumber]
                FOUND_FLAG = False
                for span in lines['spans']:
                    if utils.contains_rect(span['bbox'], word_rect):
                        properties = {
                            "size": span['size'],
                            'font': span['font'],
                            'color': span['color'],
                            'flags': span['flags'],
                            'ascender': span['ascender'],
                            'descender': span['ascender'],
                        }
                        properties_str = json.dumps(properties)
                        for level, styles in level_styles.items():
                            if properties_str in styles:
                                FOUND_FLAG = True
                                if last_block == -1 or last_block == blocknumber:
                                    if last_level == -1 or level == last_level:
                                        temp = f"{temp} {text}"
                                    else:
                                        if temp.strip():
                                            toc.append([last_level, temp.strip(), page_index+1])
                                        temp = text
                                else:
                                    if temp.strip():
                                        toc.append([last_level, temp.strip(), page_index+1])
                                    temp = text

                                last_level = level
                                last_block = blocknumber
                                break
                        break
                if not FOUND_FLAG:
                    if temp.strip():
                        toc.append([last_level, temp.strip(), page_index+1])
                        last_level = -1
                    temp = ""
                    last_level = -1
                    last_block = -1
        # 校正层级
        levels = [v[0] for v in toc]
        diff = [levels[i+1]-levels[i] for i in range(len(levels)-1)]
        indices = [i for i in range(len(diff)) if diff[i] > 1]
        for idx in indices:
            toc[idx][0] = toc[idx+1][0]

        logger.debug(toc)
        
        p = Path(doc_path)
        if output_path is None:
            output_path = str(p.parent / f"{p.stem}-生成目录版.pdf")
        
        doc.set_toc(toc)
        doc.save(output_path, garbage=3, deflate=True)
        utils.dump_json(cmd_output_path, {"status": "success", "message": ""})
    except:
        p = Path(doc_path)
        toc_output_path = str(p.parent / f"{p.stem}-目录.txt")
        with open(toc_output_path, "w", encoding='utf-8') as f:
            for line in toc:
                indent = (line[0]-1)*"\t"
                f.writelines(f"{indent}{line[1]} {line[2]}\n")
        logger.error(traceback.format_exc())
        utils.dump_json(cmd_output_path, {"status": "error", "message": f"请在'{toc_output_path}'中查看目录识别结果！\n" + traceback.format_exc()})
