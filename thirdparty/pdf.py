import argparse
import json
import math
import re
import traceback
from pathlib import Path
from typing import List, Tuple, Union

import fitz
from PIL import Image, ImageChops, ImageDraw, ImageEnhance, ImageFont, ImageOps
from reportlab.lib import units
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.pdfgen import canvas

pdfmetrics.registerFont(TTFont('msyh','msyh.ttc'))
pdfmetrics.registerFont(TTFont('simkai','simkai.ttf'))

def title_preprocess(title: str):
    """提取标题层级和标题内容
    """
    try:
        title = title.rstrip()
        res = {}
        # 优先根据缩进匹配
        if title.startswith("\t"):
            m = re.match("(\t*)\s*(.+)", title)
            res['text'] = f"{m.group(2)}".rstrip()
            res['level'] = len(m.group(1))+1
            return res

        # 匹配：1.1.1 标题
        m = re.match("\s*((\d+\.?)+)\s*(.+)", title)
        if m is not None:
            res['text'] = f"{m.group(1)} {m.group(3)}"
            res['level'] = len([v for v in m.group(1).split(".") if v])
            return res
        
        # 匹配：第1章 标题
        m = re.match("\s*(第.+[章|编])\s*(.+)", title)
        if m is not None:
            res['text'] = f"{m.group(1)} {m.group(2)}"
            res['level'] = 1
            return res

        # 匹配：第1节 标题
        m = re.match("\s*(第.+节)\s*(.+)", title)
        if m is not None:
            res['text'] = f"{m.group(1)} {m.group(2)}"
            res['level'] = 2
            return res
        
        # 无匹配
        res['text'] = title
        res['level'] = 1
        return res
    except:
        traceback.print_exc()
        return {'level': 1, "text": title}

def add_toc_from_file(toc_path: str, doc_path: str, offset: int, output_path: str = None):
    """从目录文件中导入书签到pdf文件(若文件中存在行没指定页码则按1算)

    Args:
        toc_path (str): 目录文件路径
        doc_path (str): pdf文件路径
        offset (int): 偏移量, 计算方式: “pdf文件实际页码” - “目录文件标注页码”
    """
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
                toc.append([level, title, pno])
    elif toc_path.suffix == ".json":
        with open(toc_path, "r", encoding="utf-8") as f:
            toc = json.load(f)
    else:
        raise ValueError("不支持的toc文件格式!")
    # 校正层级
    levels = [v[0] for v in toc]
    diff = [levels[i+1]-levels[i] for i in range(len(levels)-1)]
    indices = [i for i in range(len(diff)) if diff[i] > 1]
    for idx in indices:
        toc[idx][0] = toc[idx+1][0]
    doc.set_toc(toc)
    if output_path is None:
        output_path = str(p.parent / f"{p.stem}-toc.pdf")
    doc.save(output_path)

def add_toc_by_gap(doc_path: str, gap: int = 1, format: str = "第%p页", output_path: str = None):
    doc: fitz.Document = fitz.open(doc_path)
    p = Path(doc_path)
    toc = []
    for i in range(0, doc.page_count, gap):
        toc.append([1, format.replace("%p", str(i+1)), i+1])
    toc.append([1, format.replace("%p", str(doc.page_count)), doc.page_count])
    doc.set_toc(toc)
    if output_path is None:
        output_path = str(p.parent / f"{p.stem}-[页码书签版].pdf")
    doc.save(output_path)

def extract_toc(doc_path: str, format: str = "txt", output_path: str = None):
    doc: fitz.Document = fitz.open(doc_path)
    p = Path(doc_path)
    toc = doc.get_toc(simple=False)
    if format == "txt":
        if output_path is None:
            output_path = str(p.parent / f"{p.stem}-toc.txt")
        with open(output_path, "w", encoding="utf-8") as f:
            for line in toc:
                indent = (line[0]-1)*"\t"
                f.writelines(f"{indent}{line[1]} {line[2]}\n")
    elif format == "json":
        if output_path is None:
            output_path = str(p.parent / f"{p.stem}-toc.json")
        for i in range(len(toc)):
            try:
                toc[i][-1] = toc[i][-1]['to'].y
            except:
                toc[i][-1] = 0
        with open(output_path, "w", encoding="utf-8") as f:
            json.dump(toc, f)

def transform_toc_file(toc_path: str, is_add_indent: bool = True, is_remove_trailing_dots: bool = True, add_offset: int = 0, output_path: str = None):
    if output_path is None:
        p = Path(toc_path)
        output_path = str(p.parent / f"{p.stem}-toc-clean.txt")
    with open(toc_path, "r", encoding="utf-8") as f, open(output_path, "w", encoding="utf-8") as f2:
        for line in f:
            new_line = line
            if is_remove_trailing_dots:
                new_line = re.sub("(\.\s*)+(?=\d*\s*$)", " ", new_line)
                new_line = new_line.rstrip() + "\n"
            if is_add_indent:
                res = title_preprocess(new_line)
                new_line = (res['level']-1)*'\t' + res['text'] + "\n"
            if add_offset:
                m = re.search("(\d+)(?=\s*$)", new_line)
                if m is not None:
                    pno = int(m.group(1))
                    pno = pno + add_offset
                    new_line = new_line[:m.span()[0]-1] + f" {pno}\n"
            f2.write(new_line)

def encrypt_pdf(doc_path: str, user_password: str, owner_password: str = None, perm: List[str] = [], output_path: str = None):
    doc: fitz.Document = fitz.open(doc_path)
    p = Path(doc_path)
    full_perm_dict = {
        "打开": fitz.PDF_PERM_ACCESSIBILITY,
        "复制": fitz.PDF_PERM_COPY,
        "打印": fitz.PDF_PERM_PRINT | fitz.PDF_PERM_PRINT_HQ,
        "注释": fitz.PDF_PERM_ANNOTATE,
        "表单": fitz.PDF_PERM_FORM,
        "插入/删除页面": fitz.PDF_PERM_ASSEMBLE,
    }
    for v in perm:
        del full_perm_dict[v]
    perm_value = sum(full_perm_dict.values())
    encrypt_meth = fitz.PDF_ENCRYPT_AES_256 # strongest algorithm
    if output_path is None:
        output_path = str(p.parent / f"{p.stem}-encrypt.pdf")
    doc.save(
        output_path,
        encryption=encrypt_meth, # set the encryption method
        owner_pw=owner_password, # set the owner password
        user_pw=user_password, # set the user password
        permissions=perm_value, # set permissions
    )

def decrypt_pdf(doc_path: str, password: str, output_path: str = None):
    doc: fitz.Document = fitz.open(doc_path)
    p = Path(doc_path)
    if doc.isEncrypted:
        doc.authenticate(password)
        n = doc.page_count
        doc.select(range(n))
    if output_path is None:
        output_path = str(p.parent / f"{p.stem}-decrypt.pdf")
    doc.save(output_path)


def main():
    parser = argparse.ArgumentParser()
    sub_parsers = parser.add_subparsers()
    # 加密子命令
    encrypt_parser = sub_parsers.add_parser("encrypt", help="加密", description="加密pdf文件")
    encrypt_parser.add_argument("input_path", type=str, help="pdf文件路径")
    encrypt_parser.add_argument("--user_password", type=str, help="用户密码")
    encrypt_parser.add_argument("--owner_password", type=str, help="所有者密码")
    encrypt_parser.add_argument("--perm", type=str, nargs="+", help="权限")
    encrypt_parser.add_argument("-o", "--output", type=str, help="输出文件路径")
    encrypt_parser.set_defaults(which='encrypt')

    # 解密子命令
    decrypt_parser = sub_parsers.add_parser("decrypt", help="解密", description="解密pdf文件")
    decrypt_parser.add_argument("input_path", type=str, help="pdf文件路径")
    decrypt_parser.add_argument("--password", type=str, help="密码")
    decrypt_parser.add_argument("-o", "--output", type=str, help="输出文件路径")
    decrypt_parser.set_defaults(which='decrypt')
    
    # 书签子命令
    bookmark_parser = sub_parsers.add_parser("bookmark", help="书签", description="添加、提取、转换书签")
    bookmark_sub_parsers = bookmark_parser.add_subparsers()
    bookmark_parser.set_defaults(which='bookmark')

    ## 添加书签
    bookmark_add_parser = bookmark_sub_parsers.add_parser("add", help="添加书签")
    ### 文件书签
    bookmark_add_parser.add_argument("input_path", type=str, help="pdf文件路径")
    bookmark_add_parser.add_argument("--method", type=str, choices=['file', 'gap'], default="file", help="添加方式")
    bookmark_add_parser.add_argument("--toc", type=str, help="目录文件路径")
    bookmark_add_parser.add_argument("--offset", type=int, default=0, help="偏移量, 计算方式: “pdf文件实际页码” - “目录文件标注页码”")
    bookmark_add_parser.add_argument("-o", "--output", type=str, help="输出文件路径")
    bookmark_add_parser.set_defaults(bookmark_which='add')
    
    ### 页码书签
    bookmark_add_parser.add_argument("--gap", type=int, default=1, help="页码间隔")
    bookmark_add_parser.add_argument("--format", type=str, default="第%p页", help="页码格式")
    
    ## 提取书签
    bookmark_extract_parser = bookmark_sub_parsers.add_parser("extract", help="提取书签")
    bookmark_extract_parser.add_argument("input_path", type=str, help="pdf文件路径")
    bookmark_extract_parser.add_argument("--format", type=str, default="txt", choices=['txt', 'json'], help="输出文件格式")
    bookmark_extract_parser.add_argument("-o", "--output", type=str, help="输出文件路径")
    bookmark_extract_parser.set_defaults(bookmark_which='extract')
    
    ## 书签转换
    bookmark_transform_parser = bookmark_sub_parsers.add_parser("transform", help="转换书签")
    bookmark_transform_parser.add_argument("--toc", type=str, help="目录文件路径")
    bookmark_transform_parser.add_argument("--add_indent", action="store_true", help="是否添加缩进")
    bookmark_transform_parser.add_argument("--remove_trailing_dots", action="store_true", help="是否删除标题末尾的点号")
    bookmark_transform_parser.add_argument("--add_offset", type=int, default=0, help="页码偏移量")
    bookmark_transform_parser.add_argument("-o", "--output", type=str, help="输出文件路径")
    bookmark_transform_parser.set_defaults(bookmark_which='transform')

    # 水印子命令
    watermark_parser = sub_parsers.add_parser("watermark", help="水印", description="添加文本水印")
    watermark_parser.add_argument("input_path", type=str, help="pdf文件路径")
    watermark_parser.add_argument("--mark-text", type=str, required=True, dest="mark_text", help="水印文本")
    watermark_parser.add_argument("--font-family", type=str, dest="font_family", help="水印字体路径")
    watermark_parser.add_argument("--font-size", type=int, default=50, dest="font_size", help="水印字体大小")
    watermark_parser.add_argument("--color", type=str, default="#808080", dest="color", help="水印文本颜色")
    watermark_parser.add_argument("--angle", type=int, default=30, dest="angle", help="水印旋转角度")
    watermark_parser.add_argument("--space", type=int, default=75, dest="space", help="水印文本间距")
    watermark_parser.add_argument("--opacity", type=float, default=0.15, dest="opacity", help="水印不透明度")
    watermark_parser.add_argument("--font-height-crop", type=str, default="1.2", dest="font_height_crop")
    watermark_parser.add_argument("--quality", type=int, default=80, dest="quality", help="水印图片保存质量")
    watermark_parser.add_argument("-o", "--output", type=str, help="输出文件路径")
    watermark_parser.set_defaults(which='watermark')
    
    args = parser.parse_args()
    print(args)
    if args.which == "encrypt":
        encrypt_pdf(args.input_path, args.user_password, args.owner_password, args.perm, args.output)
    elif args.which == "decrypt":
        decrypt_pdf(args.input_path, args.password, args.output)
    elif args.which == "bookmark":
        if args.bookmark_which == "add":
            if args.method == "file":
                add_toc_from_file(args.toc, args.input_path, args.offset, args.output)
            elif args.method == "gap":
                add_toc_by_gap(args.input_path, args.gap, args.format, args.output)
        elif args.bookmark_which == "extract":
            extract_toc(args.input_path, args.format, args.output)
        elif args.bookmark_which == "transform":
            transform_toc_file(args.toc, args.add_indent, args.remove_trailing_dots, args.add_offset, args.output)
    elif args.which == "watermark":
        mark_args = {
            "font_family": args.font_family,
            "size": args.font_size,
            "space": args.space,
            "angle": args.angle,
            "color": args.color,
            "opacity": args.opacity,
            "font_height_crop": "1.2",
        }
        if args.input_path.endswith(".pdf"):
            # add_mark_to_pdf(doc_path=args.input_path, output_path=args.output, mark_text=args.mark_text, quality=args.quality, **mark_args)
            pass
        else:
            raise ValueError("不支持的文件格式!")


def test():
    doc = fitz.Document()
    page = doc.new_page()  # new or existing page via doc[n]
    p = fitz.Point(50, 72)  # start point of 1st line

    # text = "Some text,\nspread across\nseveral lines."
    # # the same result is achievable by
    # # text = ["Some text", "spread across", "several lines."]

    # rc = page.insert_text(p,  # bottom-left of 1st char
    #                     text,  # the text (honors '\n')
    #                     fontname = "helv",  # the default font
    #                     fontsize = 11,  # the default font size
    #                     rotate = 90,  # also available: 90, 180, 270
    #                     )
    # print("%i lines printed on page %i." % (rc, page.number))

    rect = fitz.Rect(100, 100, 200, 200)  # 设置文本框的位置和大小
    annot = page.new_annot('Text', rect)

    annot.update(fontsize=12, font='Times-Bold', color=(0, 0, 1))  # 设置字体、字号、颜色等属性
    annot.set_rotation(30)  # 设置旋转角度
    annot.content = 'Hello, world!'  # 插入文本
    doc.save("text.pdf")
    

def embed():
    doc = fitz.open("text.pdf") # open main document
    embedded_doc = fitz.open("pdf2-0.pdf") # open document you want to embed

    embedded_data = embedded_doc.tobytes() # get the document byte data as a buffer

    # embed with the file name and the data
    doc.embfile_add("my-embedded_file.pdf", embedded_data)

    doc.save("document-with-embed.pdf") # save the document

def create_wartmark(content:str,
                    filename:str,
                    width: Union[int, float],
                    height: Union[int, float],
                    font: str,
                    fontsize: int,
                    angle: Union[int, float] = 45,
                    text_stroke_color_rgb: Tuple[int, int, int] = (0, 0, 0),
                    text_fill_color_rgb: Tuple[int, int, int] = (0, 0, 0),
                    text_fill_alpha: Union[int, float] = 1) -> None:
    #创建PDF文件，指定文件名及尺寸，以像素为单位
    c = canvas.Canvas(f'{filename}.pdf',pagesize=(width*units.mm,height*units.mm))

    #画布平移保证文字完整性
    c.translate(0.1*width*units.mm,0.1*height*units.mm)

    #设置旋转角度
    # c.rotate(angle)

    #设置字体大小
    c.setFont(font,fontsize)

    #设置字体轮廓彩色
    c.setStrokeColorRGB(*text_stroke_color_rgb)

    #设置填充色
    c.setFillColorRGB(*text_fill_color_rgb)

    #设置字体透明度
    c.setFillAlpha(text_fill_alpha)

    #绘制字体内容
    c.drawString(0,0,content)
    # c.setPageRotation(45)
    c.setCropBox([0, 0, 100*units.mm, 30*units.mm])

    #保存文件
    c.save()

if __name__ == "__main__":
    main()
    # test()
    # embed()
    # create_wartmark(content='关注carl_奕然，学习更多有趣的python知识',
                #  filename='小鱼watermarkDemo6',
                #  width=2*200,
                #  height=200,
                #  font='simkai',
                #  fontsize=35,
                #  text_fill_alpha=0.3) 