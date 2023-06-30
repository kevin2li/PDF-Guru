import json
import re
import traceback
from pathlib import Path
import argparse
from typing import List
import fitz
from PIL import Image, ImageChops, ImageDraw, ImageEnhance, ImageFont, ImageOps
import math

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

def set_opacity(im, opacity):
    '''
    设置水印透明度
    '''
    assert opacity >= 0 and opacity <= 1

    alpha = im.split()[3]
    alpha = ImageEnhance.Brightness(alpha).enhance(opacity)
    im.putalpha(alpha)
    return im

def crop_image(im):
    '''裁剪图片边缘空白'''
    bg = Image.new(mode='RGBA', size=im.size)
    diff = ImageChops.difference(im, bg)
    del bg
    bbox = diff.getbbox()
    if bbox:
        return im.crop(bbox)
    return im


def gen_mark(
    mark_text       : str,
    font_family     : str,
    size            : int = 50,
    space           : int = 75,
    angle           : int = 30,
    color           : str = "#808080",
    opacity         : float=0.15,
    font_height_crop: str="1.2",
    ): 
    """生成水印图片，返回添加水印的函数

    Args:
        mark_text (str): 水印文本
        size (int, optional): font size of text. Defaults to 50.
        space (int, optional): space between watermarks. Defaults to 75.
        angle (int, optional): rotate angle of watermarks. Defaults to 30.
        color (str, optional): text color. Defaults to "#808080".
        opacity (float, optional): opacity of watermarks. Defaults to 0.15.
        font_height_crop (float, optional): change watermark font height crop float will be parsed to factor; int will be parsed to value default is '1.2', meaning 1.2 times font size this useful with CJK font, because line height may be higher than size. Defaults to 1.2.
        font_family (str, optional): font family of text. Defaults to "../assets/青鸟华光简琥珀.ttf".
    """    
    # 字体宽度、高度
    is_height_crop_float = '.' in font_height_crop  # not good but work
    width = len(mark_text) * size
    if is_height_crop_float:
        height = round(size * float(font_height_crop))
    else:
        height = int(font_height_crop)

    # 创建水印图片(宽度、高度)
    mark = Image.new(mode='RGBA', size=(width, height))

    # 生成文字
    draw_table = ImageDraw.Draw(im=mark)
    draw_table.text(xy=(0, 0),
                    text=mark_text,
                    fill=color,
                    font=ImageFont.truetype(font_family, size=size, encoding="utf-8"))
    del draw_table

    # 裁剪空白
    mark = crop_image(mark)

    # 透明度
    set_opacity(mark, opacity)

    def mark_im(im):
        ''' 在im图片上添加水印 im为打开的原图'''

        # 计算斜边长度
        c = int(math.sqrt(im.size[0] * im.size[0] + im.size[1] * im.size[1]))

        # 以斜边长度为宽高创建大图（旋转后大图才足以覆盖原图）
        mark2 = Image.new(mode='RGBA', size=(c, c))

        # 在大图上生成水印文字，此处mark为上面生成的水印图片
        y, idx = 0, 0
        while y < c:
            # 制造x坐标错位
            x = -int((mark.size[0] + space) * 0.5 * idx)
            idx = (idx + 1) % 2

            while x < c:
                # 在该位置粘贴mark水印图片
                mark2.paste(mark, (x, y))
                x = x + mark.size[0] + space
            y = y + mark.size[1] + space

        # 将大图旋转一定角度
        mark2 = mark2.rotate(angle)

        # 在原图上添加大图水印
        if im.mode != 'RGBA':
            im = im.convert('RGBA')
        im.paste(mark2, (int((im.size[0] - c) / 2), int((im.size[1] - c) / 2)), mask=mark2.split()[3])
        del mark2
        return im

    return mark_im


def add_mark_to_image(img_path, mark_text: str, quality: int = 80, output_path: str = None, **mark_args):
    im = Image.open(img_path)
    im = ImageOps.exif_transpose(im)
    mark_func = gen_mark(mark_text, **mark_args)
    image = mark_func(im)
    if output_path is None:
        p = Path(img_path)
        output_path = p.parent / f"{p.stem}-watermarked{p.suffix}"
    image.save(output_path, quality=quality)

def add_mark_to_pdf(doc_path: str, mark_text: str, quality: int = 80, output_path: str = None, **mark_args):
    doc: fitz.Document = fitz.open(doc_path)
    p = Path(doc_path)
    tmp_dir = p.parent / 'tmp'
    tmp_dir.mkdir(parents=True, exist_ok=True)
    page = doc.load_page(0)
    blank = Image.new("RGB", (int(page.rect[2]), int(page.rect[3])), (255, 255, 255))
    blank_savepath = tmp_dir / "blank.png"
    blank.save(blank_savepath)
    mark_savepath = tmp_dir / "watermark.png"
    add_mark_to_image(blank_savepath, mark_text, quality=quality, output_path=mark_savepath, **mark_args)

    for page_index in range(doc.page_count):
        page = doc[page_index]
        page.insert_image(
            page.rect,                  # where to place the image (rect-like)
            filename=mark_savepath,     # image in a file
            overlay=False,          # put in foreground
        )
    if output_path is None:
        p = Path(doc_path)
        output_path = p.parent / f"{p.stem}-watermarked{p.suffix}"
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
    bookmark_add_parser.add_argument("input_path", type=str, help="pdf文件路径")
    bookmark_add_parser.add_argument("--toc", type=str, required=True, help="目录文件路径")
    bookmark_add_parser.add_argument("--offset", type=int, default=0, help="偏移量, 计算方式: “pdf文件实际页码” - “目录文件标注页码”")
    bookmark_add_parser.add_argument("-o", "--output", type=str, help="输出文件路径")
    bookmark_add_parser.set_defaults(bookmark_which='add')
    
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
            add_toc_from_file(args.toc, args.input_path, args.offset, args.output)
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
            add_mark_to_pdf(doc_path=args.input_path, output_path=args.output, mark_text=args.mark_text, quality=args.quality, **mark_args)
        elif args.input_path.endswith(".png") or args.input_path.endswith(".jpg") or args.input_path.endswith(".jpeg"):
            add_mark_to_image(img_path=args.input_path, output_path=args.output, mark_text=args.mark_text, quality=args.quality, **mark_args)
        else:
            raise ValueError("不支持的文件格式!")

if __name__ == "__main__":
    main()