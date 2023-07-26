import json
import traceback
from pathlib import Path
from typing import Dict, List

import fitz
import utils
from constants import cmd_output_path
from loguru import logger
import requests
from uuid import uuid4
from PIL import Image, ImageDraw

# Anki connect
# Document: https://foosoft.net/projects/anki-connect/

def request(action, **params):
    return {'action': action, 'params': params, 'version': 6}

# def invoke(address: str = "http://localhost:8765", action: str = "deckNames", **params):
#     requestJson = json.dumps(request(action, **params)).encode('utf-8')
#     response = json.load(urllib.request.urlopen(urllib.request.Request(address, requestJson)))
#     logger.debug(response)
#     if len(response) != 2:
#         raise Exception('response has an unexpected number of fields')
#     if 'error' not in response:
#         raise Exception('response is missing required error field')
#     if 'result' not in response:
#         raise Exception('response is missing required result field')
#     if response['error'] is not None:
#         raise Exception(response['error'])
#     return response['result']

def invoke(address, action, **params):
    data = {
        "action": action,
        "version": 6,
        "params": params
    }
    resp = requests.post(address, json=data)
    if resp.status_code != 200:
        raise Exception(f"Anki Connect Error: {resp.status_code}")
    else:
        resp_json = resp.json()
        if resp_json['error'] is not None:
            raise Exception(resp_json['error'])
        else:
            return resp_json['result']

def get_deck_names(address: str = "http://localhost:8765"):
    try:
        res = invoke(address=address, action="deckNames")
        utils.dump_json(cmd_output_path, {"status": "success", "message": "", "data": res})
    except:
        logger.error(traceback.format_exc())
        utils.dump_json(cmd_output_path, {"status": "error", "message": traceback.format_exc()})

def anki_card_by_image_mask(
        doc_path: str,
        address: str = "http://127.0.0.1:8765",
        parent_deck: str = "",
        mode: List[str] = ["hide_one_guess_one", "hide_all_guess_one", "hide_all_guess_all"],
        q_mask_color: str = "#ff5656",
        a_mask_color: str = "#ffeba2",
        dpi: int = 300,
        tags: List[str] = [],
        page_range: str = "all",
        output_path: str = None
    ):
    try:
        doc: fitz.Document = fitz.open(doc_path)
        roi_indices = utils.parse_range(page_range, doc.page_count)
        media_dir = Path(invoke(address=address, action="getMediaDirPath"))
        if output_path is None:
            output_dir = media_dir
        RECT_ANNOT_FLAG = False
        cards = []
        fields = ["ID (hidden)", "Header", "Image", "Question Mask", "Footer", "Remarks", "Sources", "Extra 1", "Extra 2", "Answer Mask", "Original Mask"]
        for page_index in roi_indices:
            page = doc[page_index]
            annot_objs = []
            for annot in page.annots():
                if annot.type[0] == fitz.PDF_ANNOT_SQUARE or annot.type[0] == fitz.PDF_ANNOT_HIGHLIGHT: # Square
                    RECT_ANNOT_FLAG = True
                    obj = {
                        "rect": annot.rect,
                        "page": page_index,
                    }
                    # rect_list.append(annot.rect)
                    annot_objs.append(obj)
                page.delete_annot(annot)
            if not annot_objs:
                continue
            card = {k: "" for k in fields}
            origin_img = page.get_pixmap(matrix=fitz.Matrix(dpi/72, dpi/72), alpha=False)
            new_w, new_h = origin_img.width, origin_img.height
            factor = new_w / page.rect.width
            origin_mask_img = Image.new('RGBA', (new_w, new_h), (0, 0, 0, 0))
            draw = ImageDraw.Draw(origin_mask_img)

            for i, obj in enumerate(annot_objs):
                rect = obj['rect']
                bbox = [v*factor for i, v in enumerate(rect)]
                draw.rectangle(bbox, fill=q_mask_color)
            uid = uuid4()
            origin_img_path = str(output_dir / f"{uid}_pdfguru-origin_img.png")
            origin_mask_img_path = str(output_dir / f"{uid}_pdfguru-origin_mask_img.png")
            origin_img.save(origin_img_path)
            origin_mask_img.save(str(output_dir / f"{uid}_pdfguru-origin_mask_img.png"))

            # 遮全猜全
            if "hide_all_guess_all" in mode:
                a_img = Image.new('RGBA', (new_w, new_h), (0, 0, 0, 0))
                a_mask_path = str(output_dir / f"{uid}_pdfguru_all_answer_mask_img.png")
                a_img.save(a_mask_path)
                card.update({
                    "ID (hidden)": str(uid)+f"-all",
                    "Image": f'<img src="{str(Path(origin_img_path).relative_to(media_dir))}" />',
                    "Question Mask": f'<img src="{str(Path(origin_mask_img_path).relative_to(media_dir))}" />',
                    "Answer Mask": f'<img src="{str(Path(a_mask_path).relative_to(media_dir))}" />',
                    "Original Mask": f'<img src="{str(Path(origin_mask_img_path).relative_to(media_dir))}" />',
                })
                cards.append(card.copy())

            # 遮一猜一
            if "hide_one_guess_one" in mode:
                a_img = Image.new('RGBA', (new_w, new_h), (0, 0, 0, 0))
                a_mask_path = str(output_dir / f"{uid}_pdfguru_single_answer_mask_img.png")
                a_img.save(a_mask_path)
                for i, obj in enumerate(annot_objs):
                    rect = obj['rect']
                    q_img = Image.new('RGBA', (new_w, new_h), (0, 0, 0, 0))
                    q_draw = ImageDraw.Draw(q_img)
                    bbox = [v*factor for i, v in enumerate(rect)]
                    q_draw.rectangle(bbox, fill=q_mask_color)
                    q_mask_path = str(output_dir / f"{uid}_pdfguru_single_question_mask_img_{i}.png")
                    q_img.save(q_mask_path)
                    card.update({
                        "ID (hidden)": str(uid)+f"-single-{i}",
                        "Image": f'<img src="{str(Path(origin_img_path).relative_to(media_dir))}" />',
                        "Question Mask": f'<img src="{str(Path(q_mask_path).relative_to(media_dir))}" />',
                        "Answer Mask": f'<img src="{str(Path(a_mask_path).relative_to(media_dir))}" />',
                        "Original Mask": f'<img src="{str(Path(origin_mask_img_path).relative_to(media_dir))}" />',
                    })

                    cards.append(card.copy())
            
            # 遮全猜一
            if "hide_all_guess_one" in mode:
                for i, obj in enumerate(annot_objs):
                    rect = obj['rect']
                    q_img = Image.new('RGBA', (new_w, new_h), (0, 0, 0, 0))
                    a_img = Image.new('RGBA', (new_w, new_h), (0, 0, 0, 0))
                    q_draw = ImageDraw.Draw(q_img)
                    a_draw = ImageDraw.Draw(a_img)
                    for j in range(len(annot_objs)):
                        bbox = [v*factor for idx, v in enumerate(annot_objs[j]['rect'])]
                        if j != i:
                            q_draw.rectangle(bbox, fill=a_mask_color)
                            a_draw.rectangle(bbox, fill=a_mask_color)
                        else:
                            q_draw.rectangle(bbox, fill=q_mask_color)
                    q_mask_path = str(output_dir / f"{uid}_pdfguru_multi_question_mask_img_{i}.png")
                    q_img.save(q_mask_path)
                    a_mask_path = str(output_dir / f"{uid}_pdfguru_multi_answer_mask_img_{i}.png")
                    a_img.save(a_mask_path)
                    card.update({
                        "ID (hidden)": str(uid)+f"-multi-{i}",
                        "Image": f'<img src="{str(Path(origin_img_path).relative_to(media_dir))}" />',
                        "Question Mask": f'<img src="{str(Path(q_mask_path).relative_to(media_dir))}" />',
                        "Answer Mask": f'<img src="{str(Path(a_mask_path).relative_to(media_dir))}" />',
                        "Original Mask": f'<img src="{str(Path(origin_mask_img_path).relative_to(media_dir))}" />',
                    })
                    cards.append(card.copy())
        # logger.debug(cards)
        if not RECT_ANNOT_FLAG:
            logger.error("没有发现矩形注释！")
            utils.dump_json(cmd_output_path, {"status": "error", "message": "没有发现矩形注释！"})
            return
        if not cards:
            logger.error("没有发现卡片！")
            utils.dump_json(cmd_output_path, {"status": "error", "message": "没有发现卡片！"})
            return

        if not parent_deck:
            parent_deck = Path(doc_path).stem
            try:
                res = invoke(address=address, action="createDeck", deck=parent_deck)
                logger.debug(f"createDeck: {parent_deck} res: {res}")
            except:
                utils.dump_json(cmd_output_path, {"status": "error", "message": traceback.format_exc()})
                return
        notes = []
        for i, card in enumerate(cards):
            item = {
                "deckName": parent_deck,
                "modelName": "Image Occlusion Enhanced",
                "fields": card,
                "tags": tags,
                "options": {
                    "allowDuplicate": False,
                    "duplicateScope": "deck",
                },
            }
            notes.append(item)
        res = invoke(address=address, action="addNotes", notes=notes)
        logger.debug(res)
        utils.dump_json(cmd_output_path, {"status": "success", "message": ""})
    except:
        logger.error(traceback.format_exc())
        utils.dump_json(cmd_output_path, {"status": "error", "message": traceback.format_exc()})


def anki_card_by_rect_annots(
        doc_path: str,
        address: str = "http://127.0.0.1:8765",
        parent_deck: str = "",
        is_create_sub_deck: bool = True,
        level: int = 2,
        mode: List[str] = ["hide_one_guess_one", "hide_all_guess_one", "hide_all_guess_all"],
        q_mask_color: str = "#ff5656",
        a_mask_color: str = "#ffeba2",
        dpi: int = 300,
        tags: List[str] = [],
        mask_types: List[str] = ["highlight", "underline", "squiggly", "strikeout"],
        page_range: str = "all",
        output_path: str = None
    ):
    try:
        doc: fitz.Document = fitz.open(doc_path)
        roi_indices = utils.parse_range(page_range, doc.page_count)
        media_dir = Path(invoke(address=address, action="getMediaDirPath"))
        if output_path is None:
            output_dir = media_dir
        toc = doc.get_toc(simple=True)
        RECT_ANNOT_FLAG = False
        cards = []
        decks = []
        fields = ["ID (hidden)", "Header", "Image", "Question Mask", "Footer", "Remarks", "Sources", "Extra 1", "Extra 2", "Answer Mask", "Original Mask"]
        for page_index in roi_indices:
            page = doc[page_index]
            annot_objs = []
            highlight_objs = []
            underline_objs = []
            squiggly_objs = []
            strokeout_objs = []
            for annot in page.annots():
                logger.debug(annot)
                if annot.type[0] == fitz.PDF_ANNOT_SQUARE:
                    RECT_ANNOT_FLAG = True
                    obj = {
                        "rect": annot.rect,
                        "page": page_index,
                    }
                    # rect_list.append(annot.rect)
                    annot_objs.append(obj)
                elif annot.type[0] == fitz.PDF_ANNOT_HIGHLIGHT:
                    obj = {
                        "rect": annot.rect,
                        "page": page_index,
                    }
                    highlight_objs.append(obj)
                elif annot.type[0] == fitz.PDF_ANNOT_UNDERLINE:
                    obj = {
                        "rect": annot.rect,
                        "page": page_index,
                    }
                    underline_objs.append(obj)
                elif annot.type[0] == fitz.PDF_ANNOT_SQUIGGLY:
                    obj = {
                        "rect": annot.rect,
                        "page": page_index,
                    }
                    squiggly_objs.append(obj)
                elif annot.type[0] == fitz.PDF_ANNOT_STRIKE_OUT:
                    obj = {
                        "rect": annot.rect,
                        "page": page_index,
                    }
                    strokeout_objs.append(obj)
                page.delete_annot(annot)
            if not annot_objs:
                continue
            while annot_objs:
                card = {k: "" for k in fields}
                deck = parent_deck
                annot_objs.sort(key=lambda x: (x['rect'][1], x['rect'][0])) # find most top and left rect
                used = [False] * len(annot_objs)
                used[0] = True
                max_rect = annot_objs[0]['rect']
                w, h = int(max_rect[2]-max_rect[0]), int(max_rect[3]-max_rect[1])
                logger.debug(f"max_rect: {max_rect}")
                if w == 0: # 无效矩形
                    annot_objs = [rect for i, rect in enumerate(annot_objs) if not used[i]]
                    continue
                origin_img = page.get_pixmap(matrix=fitz.Matrix(dpi/72, dpi/72), clip=max_rect, alpha=False)
                new_w, new_h = origin_img.width, origin_img.height
                factor = new_w / w
                origin_mask_img = Image.new('RGBA', (new_w, new_h), (0, 0, 0, 0))
                draw = ImageDraw.Draw(origin_mask_img)
                inner_rect_list = []
                for i, obj in enumerate(annot_objs):
                    rect = obj['rect']
                    if not used[i] and utils.contains_rect(max_rect, rect):
                        bbox = [(v-max_rect[i%2])*factor for i, v in enumerate(rect)]
                        draw.rectangle(bbox, fill=q_mask_color)
                        used[i] = True
                        inner_rect_list.append(rect)
                other_objs = []
                if 'highlight' in mask_types:
                    other_objs += highlight_objs
                if 'underline' in mask_types:
                    other_objs += underline_objs
                if 'squiggly' in mask_types:
                    other_objs += squiggly_objs
                if 'strikeout' in mask_types:
                    other_objs += strokeout_objs
                for i, obj in enumerate(other_objs):
                    rect = obj['rect']
                    if utils.contains_rect(max_rect, rect):
                        bbox = [(v-max_rect[i%2])*factor for i, v in enumerate(rect)]
                        draw.rectangle(bbox, fill=q_mask_color)
                        inner_rect_list.append(rect)

                logger.debug(f"inner_rect_list: {inner_rect_list}")
                if not len(inner_rect_list): # 内部不含有小矩形或高亮
                    annot_objs = [rect for i, rect in enumerate(annot_objs) if not used[i]]
                    continue
                uid = uuid4()
                origin_img_path = str(output_dir / f"{uid}_pdfguru-origin_img.png")
                origin_mask_img_path = str(output_dir / f"{uid}_pdfguru-origin_mask_img.png")
                origin_img.save(origin_img_path)
                origin_mask_img.save(str(output_dir / f"{uid}_pdfguru-origin_mask_img.png"))
                
                # 获取当前书签标题
                cur_level_title_list = [""] * 3
                FLAG = False
                for i, item in enumerate(toc):
                    cur_level, title, pno = item
                    if cur_level == 1:
                        cur_level_title_list[0] = title
                        cur_level_title_list[1] = ""
                        cur_level_title_list[2] = ""
                    elif cur_level == 2:
                        cur_level_title_list[1] = title
                        cur_level_title_list[2] = ""
                    elif cur_level == 3:
                        cur_level_title_list[2] = title

                    if (page_index+1) >= pno:
                        FLAG = True
                        if level == 1:
                            deck = f"{parent_deck}::{cur_level_title_list[0]}"
                        elif level == 2:
                            deck = f"{parent_deck}::{cur_level_title_list[0]}"
                            if cur_level_title_list[1]:
                                deck = f"{deck}::{cur_level_title_list[1]}"
                        elif level == 3:
                            deck = f"{parent_deck}::{cur_level_title_list[0]}"
                            if cur_level_title_list[1]:
                                deck = f"{deck}::{cur_level_title_list[1]}"
                                if cur_level_title_list[2]:
                                    deck = f"{deck}::{cur_level_title_list[2]}"
                    else:
                        if FLAG:
                            break

                # 遮全猜全
                if "hide_all_guess_all" in mode:
                    a_img = Image.new('RGBA', (new_w, new_h), (0, 0, 0, 0))
                    a_mask_path = str(output_dir / f"{uid}_pdfguru_all_answer_mask_img.png")
                    a_img.save(a_mask_path)
                    card.update({
                        "ID (hidden)": str(uid)+f"-all",
                        "Image": f'<img src="{str(Path(origin_img_path).relative_to(media_dir))}" />',
                        "Question Mask": f'<img src="{str(Path(origin_mask_img_path).relative_to(media_dir))}" />',
                        "Answer Mask": f'<img src="{str(Path(a_mask_path).relative_to(media_dir))}" />',
                        "Original Mask": f'<img src="{str(Path(origin_mask_img_path).relative_to(media_dir))}" />',
                    })
                    cards.append(card.copy())
                    decks.append(deck)

                # 遮一猜一
                if "hide_one_guess_one" in mode:
                    a_img = Image.new('RGBA', (new_w, new_h), (0, 0, 0, 0))
                    a_mask_path = str(output_dir / f"{uid}_pdfguru_single_answer_mask_img.png")
                    a_img.save(a_mask_path)
                    for i, rect in enumerate(inner_rect_list):
                        q_img = Image.new('RGBA', (new_w, new_h), (0, 0, 0, 0))
                        q_draw = ImageDraw.Draw(q_img)
                        bbox = [(v-max_rect[i%2])*factor for i, v in enumerate(rect)]
                        q_draw.rectangle(bbox, fill=q_mask_color)
                        q_mask_path = str(output_dir / f"{uid}_pdfguru_single_question_mask_img_{i}.png")
                        q_img.save(q_mask_path)
                        card.update({
                            "ID (hidden)": str(uid)+f"-single-{i}",
                            "Image": f'<img src="{str(Path(origin_img_path).relative_to(media_dir))}" />',
                            "Question Mask": f'<img src="{str(Path(q_mask_path).relative_to(media_dir))}" />',
                            "Answer Mask": f'<img src="{str(Path(a_mask_path).relative_to(media_dir))}" />',
                            "Original Mask": f'<img src="{str(Path(origin_mask_img_path).relative_to(media_dir))}" />',
                        })
                        cards.append(card.copy())
                        decks.append(deck)

                # 遮全猜一
                if "hide_all_guess_one" in mode:
                    for i, rect in enumerate(inner_rect_list):
                        q_img = Image.new('RGBA', (new_w, new_h), (0, 0, 0, 0))
                        a_img = Image.new('RGBA', (new_w, new_h), (0, 0, 0, 0))
                        q_draw = ImageDraw.Draw(q_img)
                        a_draw = ImageDraw.Draw(a_img)
                        for j in range(len(inner_rect_list)):
                            bbox = [(v-max_rect[idx%2])*factor for idx, v in enumerate(inner_rect_list[j])]
                            if j != i:
                                q_draw.rectangle(bbox, fill=a_mask_color)
                                a_draw.rectangle(bbox, fill=a_mask_color)
                            else:
                                q_draw.rectangle(bbox, fill=q_mask_color)
                        q_mask_path = str(output_dir / f"{uid}_pdfguru_multi_question_mask_img_{i}.png")
                        q_img.save(q_mask_path)
                        a_mask_path = str(output_dir / f"{uid}_pdfguru_multi_answer_mask_img_{i}.png")
                        a_img.save(a_mask_path)
                        card.update({
                            "ID (hidden)": str(uid)+f"-multi-{i}",
                            "Image": f'<img src="{str(Path(origin_img_path).relative_to(media_dir))}" />',
                            "Question Mask": f'<img src="{str(Path(q_mask_path).relative_to(media_dir))}" />',
                            "Answer Mask": f'<img src="{str(Path(a_mask_path).relative_to(media_dir))}" />',
                            "Original Mask": f'<img src="{str(Path(origin_mask_img_path).relative_to(media_dir))}" />',
                        })
                        cards.append(card.copy())
                        decks.append(deck)
                annot_objs = [rect for i, rect in enumerate(annot_objs) if not used[i]]

        if not RECT_ANNOT_FLAG:
            logger.error("没有发现矩形注释！")
            utils.dump_json(cmd_output_path, {"status": "error", "message": "没有发现矩形注释！"})
            return
        # utils.dump_json(output_dir / "cards.json", cards)
        if not parent_deck:
            parent_deck = Path(doc_path).stem
        logger.debug(f"parent_deck: {parent_deck}")
        logger.debug(f"cards len: {len(cards)}")
        notes = []
        logger.debug(decks)
        for i, (card, deck) in enumerate(zip(cards, decks)):
            if is_create_sub_deck:
                deckname = deck
            else:
                deckname = parent_deck
            try:
                res = invoke(address=address, action="createDeck", deck=deckname)
                logger.debug(f"createDeck: {deckname} res: {res}")
            except:
                utils.dump_json(cmd_output_path, {"status": "error", "message": traceback.format_exc()})
                return
            item = {
                "deckName": deckname,
                "modelName": "Image Occlusion Enhanced",
                "fields": card,
                "tags": tags,
                "options": {
                    "allowDuplicate": False,
                    "duplicateScope": "deck",
                },
            }
            notes.append(item)
        try:
            res = invoke(address=address, action="addNotes", notes=notes)
            logger.debug(res)
        except:
            utils.dump_json(cmd_output_path, {"status": "error", "message": traceback.format_exc()})
            return
        utils.dump_json(cmd_output_path, {"status": "success", "message": ""})
    except:
        logger.error(traceback.format_exc())
        utils.dump_json(cmd_output_path, {"status": "error", "message": traceback.format_exc()})


def anki_card_by_font_style(
        doc_path: str,
        matches: List[str] = ["same_font", "same_size", "same_color"],
        page_range: str = "all",
        output_path: str = None
    ):
    try:
        doc: fitz.Document = fitz.open(doc_path)
        roi_indicies = utils.parse_range(page_range, doc.page_count)

        annot_list = []
        for page_index in range(doc.page_count):
            page = doc[page_index]
            for annot in page.annots():
                if annot.type[0] == 4: # Square
                    annot_list.append({
                        "page": page_index,
                        "rect": annot.rect,
                    })
                    page.delete_annot(annot)
        logger.debug(annot_list)
        if not annot_list:
            logger.error("没有发现矩形注释！")
            utils.dump_json(cmd_output_path, {"status": "error", "message": "没有发现矩形注释！"})
            return
        for i, item in enumerate(annot_list):
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
                            properties = {}
                            if "same_font" in matches:
                                properties['font'] = span['font']
                            if "same_size" in matches:
                                properties['size'] = span['size']
                            if "same_color" in matches:
                                properties['color'] = span['color']
                            if "same_flags" in matches:
                                properties['flags'] = span['flags']
                            properties_str = json.dumps(properties)
                            roi_words['properties'].append(properties_str)
                            break
        logger.debug(roi_words)
        mask_styles = list(set(roi_words['properties']))
        logger.debug(mask_styles)
        if not mask_styles:
            utils.dump_json(cmd_output_path, {"status": "error", "message": "没有识别到样式！"})
            return
        for page_index in roi_indicies:
            page = doc[page_index]
            blocks = page.get_text("dict", flags=11)['blocks']
            words = page.get_text("words") # (x0, y0, x1, y1, "string", blocknumber, linenumber, wordnumber)
            begin_bbox = []
            end_bbox = []
            FOUND_BEGIN_FLAG = False
            FOUND_END_FLAG = False
            last_word_rect = None
            for idx, word in enumerate(words):
                *word_rect, text, blocknumber, linenumber, wordnumber = word
                line = blocks[blocknumber]['lines'][linenumber]
                for span in line['spans']:
                    if utils.contains_rect(span['bbox'], word_rect):
                        properties = {}
                        if "same_font" in matches:
                            properties['font'] = span['font']
                        if "same_size" in matches:
                            properties['size'] = span['size']
                        if "same_color" in matches:
                            properties['color'] = span['color']
                        if "same_flags" in matches:
                            properties['flags'] = span['flags']
                        properties_str = json.dumps(properties)
                        if properties_str in mask_styles:
                            logger.debug(word)
                            if not FOUND_BEGIN_FLAG:
                                begin_bbox = word_rect
                                FOUND_BEGIN_FLAG = True
                                logger.debug("begin")
                            if idx == len(words) - 1:
                                FOUND_END_FLAG = True
                                end_bbox = word_rect
                                logger.debug("end")
                            else:
                                *next_word_rect, next_text, next_blocknumber, next_linenumber, next_wordnumber = words[idx+1]
                                logger.debug(f"block_number: {blocknumber} {next_blocknumber} linenumber: {linenumber} {next_linenumber} next_text: {next_text}")
                                if next_blocknumber != blocknumber or next_linenumber != linenumber:
                                    end_bbox = word_rect
                                    FOUND_END_FLAG = True
                                    logger.debug("end")
                        else:
                            if FOUND_BEGIN_FLAG:
                                end_bbox = last_word_rect
                                FOUND_END_FLAG = True
                                logger.debug("end")
                        break
                if FOUND_END_FLAG:
                    mask_rect = [*begin_bbox[:2], *end_bbox[2:]]
                    logger.debug(f"page: {page_index+1}")
                    logger.debug(f"mask_rect: {mask_rect}")
                    try:
                        annot = page.add_rect_annot(fitz.Rect(*mask_rect))
                    except:
                        traceback.print_exc()
                    FOUND_BEGIN_FLAG = False
                    FOUND_END_FLAG = False
                last_word_rect = word_rect
        if output_path is None:
            p = Path(doc_path)
            output_path = p.parent / f"{p.stem}-anki.pdf"
        doc.save(output_path, garbage=4, deflate=True, clean=True)
    except:
        logger.error(traceback.format_exc())
        utils.dump_json(cmd_output_path, {"status": "error", "message": traceback.format_exc()})


def anki_qa_card(
        doc_path: str,
        address: str = "http://127.0.0.1:8765",
        parent_deck: str = "",
        model_name: str = None,
        field_mappings: Dict[str, str] = {"question": "question", 'answer': 'answer'},
        is_create_sub_deck: bool = True,
        level: int = 2,
        dpi: int = 300,
        tags: List[str] = [],
        page_range: str = "all",
        output_path: str = None
    ):
    try:
        doc: fitz.Document = fitz.open(doc_path)
        roi_indices = utils.parse_range(page_range, doc.page_count)
        media_dir = Path(invoke(address=address, action="getMediaDirPath"))
        if output_path is None:
            output_dir = media_dir
        toc = doc.get_toc(simple=True)
        cards = []
        decks = []
        annot_objs = []
        for page_index in roi_indices:
            page = doc[page_index]
            for annot in page.annots():
                if annot.type[0] in [fitz.PDF_ANNOT_SQUARE, fitz.PDF_ANNOT_HIGHLIGHT]:
                    obj = {
                        "rect": annot.rect,
                        "type": annot.type[0],
                        "page": page_index,
                    }
                    annot_objs.append(obj)
                    page.delete_annot(annot)
        annot_objs.sort(key=lambda x: (x['page'], x['rect'][1], x['rect'][0])) # find most top and left rect
        logger.debug(annot_objs)
        card = {"question": [], "answer": []}
        uid = uuid4()
        deck = parent_deck
        for i, obj in enumerate(annot_objs):
            if obj['type'] == fitz.PDF_ANNOT_SQUARE:
                # 获取当前书签标题
                page_index = obj['page']
                cur_level_title_list = [""] * 3
                FLAG = False
                for i, item in enumerate(toc):
                    cur_level, title, pno = item
                    if cur_level == 1:
                        cur_level_title_list[0] = title
                        cur_level_title_list[1] = ""
                        cur_level_title_list[2] = ""
                    elif cur_level == 2:
                        cur_level_title_list[1] = title
                        cur_level_title_list[2] = ""
                    elif cur_level == 3:
                        cur_level_title_list[2] = title
                    if (page_index+1) >= pno:
                        FLAG = True
                        if level == 1:
                            deck = f"{parent_deck}::{cur_level_title_list[0]}"
                        elif level == 2:
                            deck = f"{parent_deck}::{cur_level_title_list[0]}"
                            if cur_level_title_list[1]:
                                deck = f"{deck}::{cur_level_title_list[1]}"
                        elif level == 3:
                            deck = f"{parent_deck}::{cur_level_title_list[0]}"
                            if cur_level_title_list[1]:
                                deck = f"{deck}::{cur_level_title_list[1]}"
                                if cur_level_title_list[2]:
                                    deck = f"{deck}::{cur_level_title_list[2]}"
                    else:
                        if FLAG:
                            break
                if card['question'] and card["answer"]:
                    card = {"question": "<br />".join(card['question']), "answer": "<br />".join(card['answer'])}
                    cards.append(card.copy())
                    decks.append(deck)
                    card = {"question": [], "answer": []}
                    uid = uuid4()
                page = doc[obj['page']]
                question_img = page.get_pixmap(matrix=fitz.Matrix(dpi/72, dpi/72), clip=obj['rect'], alpha=False)
                question_img_path = str(output_dir / f"{uid}_pdfguru-question_img-{len(card['question'])+1}.png")
                question_img.save(question_img_path)
                card['question'].append(f'<img src="{str(Path(question_img_path).relative_to(media_dir))}" />')
            elif obj['type'] == fitz.PDF_ANNOT_HIGHLIGHT:
                page = doc[obj['page']]
                answer_img = page.get_pixmap(matrix=fitz.Matrix(dpi/72, dpi/72), clip=obj['rect'], alpha=False)
                answer_img_path = str(output_dir / f"{uid}_pdfguru-answer_img-{len(card['answer'])+1}.png")
                answer_img.save(answer_img_path)
                card['answer'].append(f'<img src="{str(Path(answer_img_path).relative_to(media_dir))}" />')
                if i == len(annot_objs) - 1:
                    card = {"question": "<br />".join(card['question']), "answer": "<br />".join(card['answer'])}
                    cards.append(card.copy())
                    decks.append(deck)
        if not cards:
            logger.error("没有发现卡片！")
            utils.dump_json(cmd_output_path, {"status": "error", "message": "没有发现卡片！"})
            return
        cards = [dict(zip(field_mappings.values(), item.values())) for item in cards]
        utils.dump_json(output_dir / "cards.json", cards)
        if not parent_deck:
            parent_deck = Path(doc_path).stem
        logger.debug(f"parent_deck: {parent_deck}")
        logger.debug(f"cards len: {len(cards)}")
        notes = []
        logger.debug(decks)
        for i, (card, deck) in enumerate(zip(cards, decks)):
            if is_create_sub_deck:
                deckname = deck
            else:
                deckname = parent_deck
            try:
                res = invoke(address=address, action="createDeck", deck=deckname)
                logger.debug(f"createDeck: {deckname} res: {res}")
            except:
                utils.dump_json(cmd_output_path, {"status": "error", "message": traceback.format_exc()})
                return
            item = {
                "deckName": deckname,
                "modelName": model_name,
                "fields": card,
                "tags": tags,
                "options": {
                    "allowDuplicate": False,
                    "duplicateScope": "deck",
                },
            }
            notes.append(item)
        try:
            res = invoke(address=address, action="addNotes", notes=notes)
            if not all(res):
                logger.error(res, "添加卡片失败！")
                utils.dump_json(cmd_output_path, {"status": "error", "message": "添加卡片失败！"})
            logger.debug(res)
        except:
            utils.dump_json(cmd_output_path, {"status": "error", "message": traceback.format_exc()})
            return
        utils.dump_json(cmd_output_path, {"status": "success", "message": ""})
    except:
        logger.error(traceback.format_exc())
        utils.dump_json(cmd_output_path, {"status": "error", "message": traceback.format_exc()})

