import argparse
import multiprocessing
import sys
import traceback

import utils
from annot import delete_annot_pdf
from background import add_doc_background_by_color, add_doc_background_by_image
from bookmark import (add_toc_by_gap, add_toc_from_file, extract_toc,
                      find_title_by_rect_annot, transform_toc_file)
from compress import compress_pdf
from constants import logpath
from convert import (convert_anydoc2pdf, convert_pdf2png, convert_pdf2svg,
                     convert_png2pdf, convert_svg2pdf, convert_to_image_pdf)
from crop import (crop_pdf_by_bbox, crop_pdf_by_page_margin,
                  crop_pdf_by_rect_annot)
from cut import combine_pdf_by_grid, cut_pdf_by_breakpoints, cut_pdf_by_grid
from dual_layer import make_dual_layer_pdf, make_dual_layer_pdf_from_image
from encrypt import (change_password_pdf, decrypt_pdf, encrypt_pdf,
                     recover_permission_pdf)
from extract import extract_pdf_images, extract_pdf_text
from header_and_footer import (insert_header_and_footer,
                               remove_header_and_footer)
from insert import insert_blank_pdf, insert_pdf, replace_pdf
from loguru import logger
from mask import mask_pdf_by_rectangle, mask_pdf_by_rectangle_annot
from merge import merge_pdf
from metadata import extract_metadata
from page_number import insert_page_number, remove_page_number
from rotate import rotate_pdf
from scale import (resize_pdf_by_dim, resize_pdf_by_paper_size,
                   resize_pdf_by_scale)
from sign import sign_img
from slice import reorder_pdf, slice_pdf
from split import split_pdf_by_chunk, split_pdf_by_page, split_pdf_by_toc
from watermark import (detect_watermark_index_helper,
                       remove_watermark_by_index, remove_watermark_by_text,
                       remove_watermark_by_type, watermark_pdf_by_image,
                       watermark_pdf_by_pdf, watermark_pdf_by_text)


def getParser():
    parser = argparse.ArgumentParser()
    sub_parsers = parser.add_subparsers()
    # 合并子命令
    merge_parser = sub_parsers.add_parser("merge", help="合并", description="合并pdf文件")
    merge_parser.set_defaults(which='merge')
    merge_parser.add_argument("input_path_list", type=str, nargs="+", help="pdf文件路径")
    merge_parser.add_argument("-o", "--output", type=str, help="输出文件路径")
    merge_parser.add_argument("--sort_method", type=str, choices=['default', 'name', 'name_digit', 'ctime', 'mtime'], default="default", help="排序方式")
    merge_parser.add_argument("--sort_direction", type=str, choices=['asc', 'desc'], default="asc", help="排序方向")

    # 拆分子命令
    split_parser = sub_parsers.add_parser("split", help="拆分", description="拆分pdf文件")
    split_parser.set_defaults(which='split')
    split_parser.add_argument("input_path", type=str, help="pdf文件路径")
    split_parser.add_argument("--mode", type=str, choices=['chunk', 'page', 'toc'], default="chunk", help="拆分模式")
    split_parser.add_argument("--page_range", type=str, default="all", help="页码范围")
    split_parser.add_argument("--chunk_size", type=int, default=10, help="拆分块大小")
    split_parser.add_argument("-o", "--output", type=str, help="输出文件路径")
    split_parser.add_argument("--toc-level", type=int, default=1, help="目录层级")

    #  删除子命令
    delete_parser = sub_parsers.add_parser("delete", help="删除", description="删除pdf文件")
    delete_parser.set_defaults(which='delete')
    delete_parser.add_argument("input_path", type=str, help="pdf文件路径")
    delete_parser.add_argument("--page_range", type=str, default="all", help="页码范围")
    delete_parser.add_argument("-o", "--output", type=str, help="输出文件路径")

    # 插入子命令
    insert_parser = sub_parsers.add_parser("insert", help="插入", description="插入pdf文件")
    insert_parser.set_defaults(which='insert')
    insert_parser.add_argument("--method", type=str, choices=['blank', 'pdf'], default="pdf", help="插入方式")
    insert_parser.add_argument("input_path1", type=str, help="被插入的pdf文件路径")
    insert_parser.add_argument("input_path2", type=str, help="插入pdf文件路径")
    insert_parser.add_argument("--insert_pos", type=int, default=0, help="插入位置页码")
    insert_parser.add_argument("--pos-type", type=str, choices=['before_first', 'after_first', 'before_last', 'after_last', 'before_custom', 'after_custom'], default="before", help="插入位置类型")
    insert_parser.add_argument("--page_range", type=str, default="all", help="插入pdf的页码范围")
    insert_parser.add_argument("--orientation", type=str, choices=['portrait', 'landscape'], default="portrait", help="纸张方向")
    insert_parser.add_argument("--paper_size", type=str, default="A4", help="纸张大小")
    insert_parser.add_argument("--count", type=int, default=1, help="插入数量")
    insert_parser.add_argument("-o", "--output", type=str, help="输出文件路径")

    # 替换子命令
    replace_parser = sub_parsers.add_parser("replace", help="替换", description="替换pdf文件")
    replace_parser.set_defaults(which='replace')
    replace_parser.add_argument("input_path1", type=str, help="被替换的pdf文件路径")
    replace_parser.add_argument("input_path2", type=str, help="替换pdf文件路径")
    replace_parser.add_argument("--src_page_range", type=str, default="all", help="页码范围")
    replace_parser.add_argument("--dst_page_range", type=str, default="all", help="页码范围")
    replace_parser.add_argument("-o", "--output", type=str, help="输出文件路径")

    # 旋转子命令
    rotate_parser = sub_parsers.add_parser("rotate", help="旋转", description="旋转pdf文件")
    rotate_parser.set_defaults(which='rotate')
    rotate_parser.add_argument("input_path", type=str, help="pdf文件路径")
    rotate_parser.add_argument("--page_range", type=str, default="all", help="页码范围")
    rotate_parser.add_argument("--angle", type=int, default=90, help="旋转角度")
    rotate_parser.add_argument("-o", "--output", type=str, help="输出文件路径")

    # 重排子命令
    reorder_parser = sub_parsers.add_parser("reorder", help="重排", description="重排pdf文件")
    reorder_parser.set_defaults(which='reorder')
    reorder_parser.add_argument("input_path", type=str, help="pdf文件路径")
    reorder_parser.add_argument("--page_range", type=str, default="all", help="页码范围")
    reorder_parser.add_argument("-o", "--output", type=str, help="输出文件路径")

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
    
    # 修改密码子命令
    change_password_parser = sub_parsers.add_parser("change_password", help="修改密码", description="修改pdf文件密码")
    change_password_parser.set_defaults(which="change_password")
    change_password_parser.add_argument("input_path", type=str, help="pdf文件路径")
    change_password_parser.add_argument("--old_user_password", type=str, help="旧用户密码")
    change_password_parser.add_argument("--user_password", type=str, help="新用户密码")
    change_password_parser.add_argument("--old_owner_password", type=str, help="旧所有者密码")
    change_password_parser.add_argument("--owner_password", type=str, help="新所有者密码")
    change_password_parser.add_argument("-o", "--output", type=str, help="输出文件路径")

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
    bookmark_add_parser.add_argument("--page_range", type=str, default="all", help="页码范围")
    bookmark_add_parser.add_argument("--start-number", type=int, default=1, help="起始编号")

    ## 提取书签
    bookmark_extract_parser = bookmark_sub_parsers.add_parser("extract", help="提取书签")
    bookmark_extract_parser.add_argument("input_path", type=str, help="pdf文件路径")
    bookmark_extract_parser.add_argument("--format", type=str, default="txt", choices=['txt', 'json'], help="输出文件格式")
    bookmark_extract_parser.add_argument("-o", "--output", type=str, help="输出文件路径")
    bookmark_extract_parser.set_defaults(bookmark_which='extract')

    ## 书签转换
    bookmark_transform_parser = bookmark_sub_parsers.add_parser("transform", help="转换书签")
    bookmark_transform_parser.add_argument("--toc", type=str, help="目录文件路径")
    bookmark_transform_parser.add_argument("--add_offset", type=int, default=0, help="页码偏移量")
    bookmark_transform_parser.add_argument("--level-dict", type=str, action="append", help="目录层级字典")
    bookmark_transform_parser.add_argument("--delete-level-below", type=int, default=0, help="删除目录层级")
    bookmark_transform_parser.add_argument("--default-level", type=int, default=1, help="默认目录层级")
    bookmark_transform_parser.add_argument("--remove-blank-lines", action="store_true", help="删除空行")
    bookmark_transform_parser.add_argument("-o", "--output", type=str, help="输出文件路径")
    bookmark_transform_parser.set_defaults(bookmark_which='transform')

    ## 书签识别
    bookmark_detect_parser = bookmark_sub_parsers.add_parser("detect", help="识别书签")
    bookmark_detect_parser.set_defaults(bookmark_which="detect")
    bookmark_detect_parser.add_argument("--type", type=str, choices=['font', 'ocr'], default="font", help="识别方式")
    bookmark_detect_parser.add_argument("input_path", type=str, help="pdf文件路径")
    bookmark_detect_parser.add_argument("--page_range", type=str, default="all", help="页码范围")
    bookmark_detect_parser.add_argument("-o", "--output", type=str, help="输出文件路径")

    # 水印子命令
    watermark_parser = sub_parsers.add_parser("watermark", help="水印", description="添加文本水印")
    watermark_parser.set_defaults(which='watermark')

    watermark_subparsers = watermark_parser.add_subparsers()
    watermark_add_parser= watermark_subparsers.add_parser("add", help="添加水印")
    watermark_add_parser.set_defaults(watermark_which='add')
    watermark_add_parser.add_argument("input_path", type=str, help="pdf文件路径")
    watermark_add_parser.add_argument("--type", type=str, choices=['text', 'image', 'pdf'], default="text", help="水印类型")
    watermark_add_parser.add_argument("--mark-text", type=str, dest="mark_text", help="水印文本")
    watermark_add_parser.add_argument("--font-family", type=str, dest="font_family", help="水印字体路径")
    watermark_add_parser.add_argument("--font-size", type=int, default=50, dest="font_size", help="水印字体大小")
    watermark_add_parser.add_argument("--color", type=str, default="#000000", dest="color", help="水印文本颜色")
    watermark_add_parser.add_argument("--angle", type=int, default=30, dest="angle", help="水印旋转角度")
    watermark_add_parser.add_argument("--opacity", type=float, default=0.3, dest="opacity", help="水印不透明度")
    watermark_add_parser.add_argument("--line-spacing", type=float, default=1, dest="line_spacing", help="水印行间距")
    watermark_add_parser.add_argument("--word-spacing", type=float, default=1, dest="word_spacing", help="相邻水印间距")
    watermark_add_parser.add_argument("--x-offset", type=float, default=0, dest="x_offset", help="水印x轴偏移量")
    watermark_add_parser.add_argument("--y-offset", type=float, default=0, dest="y_offset", help="水印y轴偏移量")
    watermark_add_parser.add_argument("--multiple-mode", action="store_true", dest="multiple_mode", help="多行水印模式")
    watermark_add_parser.add_argument("--num-lines", type=int, default=1, dest="num_lines", help="多行水印行数")
    watermark_add_parser.add_argument("--wm-path", type=str, dest="wm_path", help="水印图片路径")
    watermark_add_parser.add_argument("--scale", type=float, default=1, dest="scale", help="水印图片缩放比例")
    watermark_add_parser.add_argument("--page_range", type=str, default="all", help="页码范围")
    watermark_add_parser.add_argument("--layer", type=str, default="bottom", help="水印图层")
    watermark_add_parser.add_argument("-o", "--output", type=str, help="输出文件路径")

    watermark_remove_parser = watermark_subparsers.add_parser("remove", help="删除水印")
    watermark_remove_parser.set_defaults(watermark_which='remove')
    watermark_remove_parser.add_argument("input_path", type=str, help="pdf文件路径")
    watermark_remove_parser.add_argument("--method", type=str, choices=['type', 'index', 'text'], default="type", help="删除方式")
    watermark_remove_parser.add_argument("--page_range", type=str, default="all", help="页码范围")
    watermark_remove_parser.add_argument("--wm_index", type=int, nargs="+", help="水印元素所有索引")
    watermark_remove_parser.add_argument("--wm_text", type=str, help="水印文本")
    watermark_remove_parser.add_argument("-o", "--output", type=str, help="输出文件路径")

    watermark_detect_parser = watermark_subparsers.add_parser("detect", help="检测水印")
    watermark_detect_parser.set_defaults(watermark_which='detect')
    watermark_detect_parser.add_argument("input_path", type=str, help="pdf文件路径")
    watermark_detect_parser.add_argument("--wm_index", type=int, default=0, help="水印所在页码")
    watermark_detect_parser.add_argument("-o", "--output", type=str, help="输出文件路径")


    # 压缩子命令
    compress_parser = sub_parsers.add_parser("compress", help="压缩", description="压缩pdf文件")
    compress_parser.add_argument("input_path", type=str, help="pdf文件路径")
    compress_parser.add_argument("-o", "--output", type=str, help="输出文件路径")
    compress_parser.set_defaults(which='compress')

    # 缩放子命令
    resize_parser = sub_parsers.add_parser("resize", help="缩放", description="缩放pdf文件")
    resize_parser.set_defaults(which='resize')
    resize_parser.add_argument("input_path", type=str, help="pdf文件路径")
    resize_parser.add_argument("--method", type=str, choices=['dim', 'scale', 'paper_size'], default="dim", help="缩放方式")
    resize_parser.add_argument("--width", type=float, help="宽度")
    resize_parser.add_argument("--height", type=float, help="高度")
    resize_parser.add_argument("--scale", type=float, help="缩放比例")
    resize_parser.add_argument("--paper_size", type=str, help="纸张大小")
    resize_parser.add_argument("--page_range", type=str, default="all", help="页码范围")
    resize_parser.add_argument("--unit", type=str, choices=['pt', 'mm', 'cm', 'in'], default="pt", help="单位")
    resize_parser.add_argument("-o", "--output", type=str, help="输出文件路径")

    # 提取子命令
    extract_parser = sub_parsers.add_parser("extract", help="提取", description="提取pdf文件")
    extract_parser.set_defaults(which='extract')
    extract_parser.add_argument("input_path", type=str, help="pdf文件路径")
    extract_parser.add_argument("--page_range", type=str, default="all", help="页码范围")
    extract_parser.add_argument("--type", type=str, choices=['text', 'image'], default="text", help="提取类型")
    extract_parser.add_argument("-o", "--output", type=str, help="输出文件路径")

    # 分割子命令
    cut_parser = sub_parsers.add_parser("cut", help="分割", description="分割pdf文件")
    cut_parser.set_defaults(which='cut')
    cut_parser.add_argument("input_path", type=str, help="pdf文件路径")
    cut_parser.add_argument("--method", type=str, choices=['grid', 'breakpoints'], default="grid", help="分割模式")
    cut_parser.add_argument("--page_range", type=str, default="all", help="页码范围")
    cut_parser.add_argument("--h_breakpoints", type=float, nargs="+", help="水平分割点")
    cut_parser.add_argument("--v_breakpoints", type=float, nargs="+", help="垂直分割点")
    cut_parser.add_argument("--nrow", type=int, default=1, help="行数")
    cut_parser.add_argument("--ncol", type=int, default=1, help="列数")
    cut_parser.add_argument("-o", "--output", type=str, help="输出文件路径")

    # 组合子命令
    combine_parser = sub_parsers.add_parser("combine", help="组合", description="组合pdf文件")
    combine_parser.set_defaults(which='combine')
    combine_parser.add_argument("input_path", type=str, help="pdf文件路径")
    combine_parser.add_argument("--page_range", type=str, default="all", help="页码范围")
    combine_parser.add_argument("--nrow", type=int, default=1, help="行数")
    combine_parser.add_argument("--ncol", type=int, default=1, help="列数")
    combine_parser.add_argument("--paper_size", type=str, default="A4", help="纸张大小")
    combine_parser.add_argument("--orientation", type=str, choices=['portrait', 'landscape'], default="portrait", help="纸张方向")
    combine_parser.add_argument("-o", "--output", type=str, help="输出文件路径")

    # 裁剪子命令
    crop_parser = sub_parsers.add_parser("crop", help="裁剪", description="裁剪pdf文件")
    crop_parser.set_defaults(which='crop')
    crop_parser.add_argument("--method", type=str, choices=['bbox', 'margin', "annot"], default="bbox", help="裁剪模式")
    crop_parser.add_argument("input_path", type=str, help="pdf文件路径")
    crop_parser.add_argument("--page_range", type=str, default="all", help="页码范围")
    crop_parser.add_argument("--bbox", type=float, nargs=4, help="裁剪框")
    crop_parser.add_argument("--margin", type=float, nargs=4, help="裁剪边距")
    crop_parser.add_argument("--keep_size", action="store_true", help="保持裁剪后的尺寸不变")
    crop_parser.add_argument("--unit", type=str, choices=['pt', 'mm', 'cm', 'in'], default="pt", help="单位")
    crop_parser.add_argument("-o", "--output", type=str, help="输出文件路径")

    # 转换子命令
    convert_parser = sub_parsers.add_parser("convert", help="转换", description="转换pdf文件")
    convert_parser.set_defaults(which='convert')
    convert_parser.add_argument("input_path", type=str, nargs="+", help="输入文件列表")
    convert_parser.add_argument("--page_range", type=str, default="all", help="页码范围")
    convert_parser.add_argument("--source-type", type=str, default="pdf", help="源类型")
    convert_parser.add_argument("--target-type", type=str, default="png", help="目标类型")
    convert_parser.add_argument("--dpi", type=int, default=300, help="分辨率")
    convert_parser.add_argument("--paper-size", type=str, default="A4", help="纸张大小")
    convert_parser.add_argument("--orientation", type=str, choices=['portrait', 'landscape'], default="portrait", help="纸张方向")
    convert_parser.add_argument("--is_merge", action="store_true", help="是否合并")
    convert_parser.add_argument("--sort-method", type=str, choices=['custom', 'name', 'name_digit', 'ctime', 'mtime'], default="default", help="排序方式")
    convert_parser.add_argument("--sort-direction", type=str, choices=['asc', 'desc'], default="asc", help="排序方向")
    convert_parser.add_argument("-o", "--output", type=str, help="输出文件路径")

    # 遮罩子命令
    mask_parser = sub_parsers.add_parser("mask", help="遮罩", description="遮罩pdf文件")
    mask_parser.set_defaults(which='mask')
    mask_parser.add_argument("input_path", type=str, help="pdf文件路径")
    mask_parser.add_argument("--page_range", type=str, default="all", help="页码范围")
    mask_parser.add_argument("--type", type=str, choices=['rect', 'annot'], default="rectangle", help="遮罩类型")
    mask_parser.add_argument("--bbox", type=float, nargs=4, action='append', help="遮罩框")
    mask_parser.add_argument("--color", type=str, default="#FFFFFF", help="遮罩颜色")
    mask_parser.add_argument("--opacity", type=float, default=0.5, help="遮罩不透明度")
    mask_parser.add_argument("--angle", type=float, default=0, help="遮罩旋转角度")
    mask_parser.add_argument("--unit", type=str, choices=['pt', 'mm', 'cm', 'in'], default="pt", help="单位")
    mask_parser.add_argument("--annot-page", type=int, default=0, help="批注所在页码")
    mask_parser.add_argument("-o", "--output", type=str, help="输出文件路径")

    # 背景子命令
    bg_parser = sub_parsers.add_parser("bg", help="背景", description="添加背景")
    bg_parser.set_defaults(which='bg')
    bg_parser.add_argument("input_path", type=str, help="pdf文件路径")
    bg_parser.add_argument("--page_range", type=str, default="all", help="页码范围")
    bg_parser.add_argument("--type", type=str, choices=['color', 'image'], default="color", help="背景类型")
    bg_parser.add_argument("--color", type=str, default="#FFFFFF", help="背景颜色")
    bg_parser.add_argument("--opacity", type=float, default=0.5, help="背景不透明度")
    bg_parser.add_argument("--angle", type=float, default=0, help="背景旋转角度")
    bg_parser.add_argument("--x-offset", type=float, default=0, help="背景x轴偏移量")
    bg_parser.add_argument("--y-offset", type=float, default=0, help="背景y轴偏移量")
    bg_parser.add_argument("--scale", type=float, default=1, help="背景缩放比例")
    bg_parser.add_argument("--img-path", type=str, help="背景图片路径")
    bg_parser.add_argument("-o", "--output", type=str, help="输出文件路径")

    # 页眉页脚子命令
    header_footer_parser = sub_parsers.add_parser("header_footer", help="页眉页脚", description="添加页眉页脚")
    header_footer_parser.set_defaults(which='header_footer')
    header_footer_parser.add_argument("--type", type=str, choices=['add', 'remove'], default="add", help="操作类型")
    header_footer_parser.add_argument("input_path", type=str, help="pdf文件路径")
    header_footer_parser.add_argument("--page-range", type=str, default="all", help="页码范围")
    header_footer_parser.add_argument("--header-left", type=str, help="页眉左侧内容")
    header_footer_parser.add_argument("--header-center", type=str, help="页眉中间内容")
    header_footer_parser.add_argument("--header-right", type=str, help="页眉右侧内容")
    header_footer_parser.add_argument("--footer-left", type=str, help="页脚左侧内容")
    header_footer_parser.add_argument("--footer-center", type=str, help="页脚中间内容")
    header_footer_parser.add_argument("--footer-right", type=str, help="页脚右侧内容")
    header_footer_parser.add_argument("--font-family", type=str, help="字体类型")
    header_footer_parser.add_argument("--font-size", type=int, default=10, help="字体大小")
    header_footer_parser.add_argument("--font-color", type=str, default="#000000", help="字体颜色")
    header_footer_parser.add_argument("--opacity", type=float, default=1, help="字体不透明度")
    header_footer_parser.add_argument("--margin-bbox", type=float, nargs=4, default=[1.27, 1.27, 2.54, 2.54], help="页眉页脚边框, [上,下,左,右]")
    header_footer_parser.add_argument("--unit", type=str, choices=['pt', 'mm', 'cm', 'in'], default="cm", help="单位")
    header_footer_parser.add_argument("--remove", type=str, nargs="+", default=['header', 'footer'], help="删除页眉页脚")
    header_footer_parser.add_argument("-o", "--output", type=str, help="输出文件路径")

    # 页码子命令
    page_number_parser = sub_parsers.add_parser("page_number", help="页码", description="添加页码")
    page_number_parser.set_defaults(which='page_number')
    page_number_parser.add_argument("input_path", type=str, help="pdf文件路径")
    page_number_parser.add_argument("--type", type=str, choices=['add', 'remove'], default="add", help="操作类型")
    page_number_parser.add_argument("--page-range", type=str, default="all", help="页码范围")
    page_number_parser.add_argument("--start", type=int, default=1, help="起始页码")
    page_number_parser.add_argument("--format", type=str, default="第%p页", help="页码格式")
    page_number_parser.add_argument("--pos", type=str, choices=['header', 'footer'], default="footer", help="页码位置")
    page_number_parser.add_argument("--align", type=str, choices=['left', 'center', 'right'], default="right", help="页码对齐方式")
    page_number_parser.add_argument("--font-family", type=str, help="字体类型")
    page_number_parser.add_argument("--font-size", type=int, default=10, help="字体大小")
    page_number_parser.add_argument("--font-color", type=str, default="#000000", help="字体颜色")
    page_number_parser.add_argument("--opacity", type=float, default=1, help="字体不透明度")
    page_number_parser.add_argument("--margin-bbox", type=float, nargs=4, help="页眉页脚边框, [上,下,左,右]")
    page_number_parser.add_argument("--unit", type=str, choices=['pt', 'mm', 'cm', 'in'], default="pt", help="单位")
    page_number_parser.add_argument("-o", "--output", type=str, help="输出文件路径")

    # 双层PDF子命令
    dual_parser = sub_parsers.add_parser("dual", help="双层PDF", description="生成双层PDF")
    dual_parser.set_defaults(which='dual')
    dual_parser.add_argument("input_path", type=str, help="pdf文件路径")
    dual_parser.add_argument("--dpi", type=int, default=300, help="分辨率")
    dual_parser.add_argument("--page-range", type=str, default="all", help="页码范围")
    dual_parser.add_argument("--lang", type=str, default="ch", help="识别语言") # ['chi_sim', 'eng']
    dual_parser.add_argument("-o", "--output", type=str, help="输出文件路径")


    # 签名子命令
    sign_parser = sub_parsers.add_parser("sign", help="签名", description="生成电子签名")
    sign_parser.set_defaults(which="sign")
    sign_parser.add_argument("input_path", type=str, help="输入图片路径")
    sign_parser.add_argument("-o", "--output", type=str, help="输出文件路径")

    # 批注子命令
    annot_parser = sub_parsers.add_parser("annot", help="批注", description="批注管理")
    annot_parser.set_defaults(which="annot")
    annot_parser.add_argument("--method", type=str, choices=['remove', 'export', 'import'], default="remove", help="操作类型")
    annot_parser.add_argument("input_path", type=str, help="pdf文件路径")
    annot_parser.add_argument("--annot-types", type=str, nargs="+", default="highlight", help="批注类型")
    annot_parser.add_argument("--page_range", type=str, default="all", help="页码范围")
    annot_parser.add_argument("-o", "--output", type=str, help="输出文件路径")
    return parser

if __name__ == "__main__":
    parser = getParser()
    args = parser.parse_args()
    try:
        logger.debug(args)
        if not args.__dict__:
            parser.print_help()
            sys.exit(0)
        if args.which == "merge":
            merge_pdf(doc_path_list=args.input_path_list, sort_method=args.sort_method, sort_direction=args.sort_direction, output_path=args.output)
        elif args.which == "split":
            if args.mode == "chunk":
                split_pdf_by_chunk(doc_path=args.input_path, chunk_size=args.chunk_size, output_path=args.output)
            elif args.mode == "page":
                split_pdf_by_page(doc_path=args.input_path, page_range=args.page_range, output_path=args.output)
            elif args.mode == "toc":
                split_pdf_by_toc(doc_path=args.input_path, level=args.toc_level, output_path=args.output)
        elif args.which == "delete":
            slice_pdf(doc_path=args.input_path, page_range=args.page_range, output_path=args.output, is_reverse=True)
        elif args.which == 'insert':
            if args.method == "blank":
                insert_blank_pdf(doc_path=args.input_path1, pos=args.insert_pos, pos_type=args.pos_type, count=args.count, orientation=args.orientation, paper_size=args.paper_size, output_path=args.output)
            else:
                insert_pdf(doc_path1=args.input_path1, doc_path2=args.input_path2, insert_pos=args.insert_pos, pos_type=args.pos_type, page_range=args.page_range, output_path=args.output)
        elif args.which == "replace":
            replace_pdf(doc_path1=args.input_path1, doc_path2=args.input_path2, src_range=args.src_page_range, dst_range=args.dst_page_range, output_path=args.output)
        elif args.which == "reorder":
            reorder_pdf(doc_path=args.input_path, page_range=args.page_range, output_path=args.output)
        elif args.which == "rotate":
            rotate_pdf(doc_path=args.input_path, angle=args.angle, page_range=args.page_range, output_path=args.output)
        elif args.which == "encrypt":
            encrypt_pdf(doc_path=args.input_path, user_password=args.user_password, owner_password=args.owner_password, perm=args.perm, output_path=args.output)
        elif args.which == "decrypt":
            if args.password:
                decrypt_pdf(doc_path=args.input_path, password=args.password, output_path=args.output)
            else:
                recover_permission_pdf(doc_path=args.input_path, output_path=args.output)
        elif args.which == "change_password":
            change_password_pdf(doc_path=args.input_path, upw=args.old_user_password, new_upw=args.user_password, opw=args.old_owner_password, new_opw=args.owner_password, output_path=args.output)
        elif args.which == "compress":
            compress_pdf(doc_path=args.input_path, output_path=args.output)
        elif args.which == "resize":
            if args.method == "dim":
                resize_pdf_by_dim(doc_path=args.input_path, width=args.width, height=args.height, unit=args.unit, page_range=args.page_range, output_path=args.output)
            elif args.method == "scale":
                resize_pdf_by_scale(doc_path=args.input_path, scale=args.scale, page_range=args.page_range, output_path=args.output)
            elif args.method == "paper_size":
                resize_pdf_by_paper_size(doc_path=args.input_path, paper_size=args.paper_size, page_range=args.page_range, output_path=args.output)
        elif args.which == "bookmark":
            if args.bookmark_which == "add":
                if args.method == "file":
                    add_toc_from_file(toc_path=args.toc, doc_path=args.input_path, offset=args.offset, output_path=args.output)
                elif args.method == "gap":
                    add_toc_by_gap(doc_path=args.input_path, gap=args.gap, format=args.format, start_number=args.start_number, page_range=args.page_range, output_path=args.output)
            elif args.bookmark_which == "extract":
                extract_toc(doc_path=args.input_path, format=args.format, output_path=args.output)
            elif args.bookmark_which == "transform":
                level_dict_list = []
                if args.level_dict:
                    for item in args.level_dict:
                        level_dict = eval(item)
                        level_dict_list.append(level_dict)
                transform_toc_file(toc_path=args.toc, level_dict_list=level_dict_list, delete_level_below=args.delete_level_below, add_offset=args.add_offset, default_level=args.default_level, is_remove_blanklines=args.remove_blank_lines, output_path=args.output)
            elif args.bookmark_which == "detect":
                if args.type == "font":
                    find_title_by_rect_annot(doc_path=args.input_path, page_range=args.page_range, output_path=args.output)
        elif args.which == "extract":
            if args.type == "text":
                extract_pdf_text(doc_path=args.input_path, page_range=args.page_range, output_path=args.output)
            elif args.type == "image":
                extract_pdf_images(doc_path=args.input_path, page_range=args.page_range, output_path=args.output)
            else:
                raise ValueError("不支持的提取类型!")
        elif args.which == "cut":
            if args.method == "grid":
                cut_pdf_by_grid(doc_path=args.input_path, n_row=args.nrow, n_col=args.ncol, page_range=args.page_range, output_path=args.output)
            elif args.method == "breakpoints":
                cut_pdf_by_breakpoints(doc_path=args.input_path, h_breakpoints=args.h_breakpoints, v_breakpoints=args.v_breakpoints, page_range=args.page_range, output_path=args.output)
        elif args.which == "combine":
            combine_pdf_by_grid(doc_path=args.input_path, n_row=args.nrow, n_col=args.ncol, paper_size=args.paper_size, orientation=args.orientation, page_range=args.page_range, output_path=args.output)
        elif args.which == "crop":
            if args.method == "bbox":
                crop_pdf_by_bbox(doc_path=args.input_path, bbox=args.bbox, unit=args.unit, keep_page_size=args.keep_size, page_range=args.page_range, output_path=args.output)
            elif args.method == "margin":
                crop_pdf_by_page_margin(doc_path=args.input_path, margin=args.margin, unit=args.unit, keep_page_size=args.keep_size, page_range=args.page_range, output_path=args.output)
            elif args.method == "annot":
                crop_pdf_by_rect_annot(doc_path=args.input_path,  keep_page_size=args.keep_size, page_range=args.page_range, output_path=args.output)
        elif args.which == "convert":
            if args.source_type == "pdf":
                if args.target_type == "png":
                    convert_pdf2png(doc_path=args.input_path, dpi=args.dpi, page_range=args.page_range,output_path=args.output)
                elif args.target_type == "svg":
                    convert_pdf2svg(doc_path=args.input_path, dpi=args.dpi, page_range=args.page_range,output_path=args.output)
                elif args.target_type == "image-pdf":
                    convert_to_image_pdf(doc_path=args.input_path, dpi=args.dpi, page_range=args.page_range,output_path=args.output)
            elif args.target_type == "pdf":
                if args.source_type == "png":
                    convert_png2pdf(input_path=args.input_path, is_merge=args.is_merge, sort_method=args.sort_method, sort_direction=args.sort_direction, paper_size=args.paper_size, orientation=args.orientation, output_path=args.output)
                elif args.source_type == "svg":
                    convert_svg2pdf(input_path=args.input_path, is_merge=args.is_merge, sort_method=args.sort_method, sort_direction=args.sort_direction, paper_size=args.paper_size, orientation=args.orientation, output_path=args.output)
                elif args.source_type == "mobi":
                    convert_anydoc2pdf(input_path=args.input_path, output_path=args.output)
                elif args.source_type == "epub":
                    convert_anydoc2pdf(input_path=args.input_path, output_path=args.output)
        elif args.which == "watermark":
            if args.watermark_which == "add":
                if args.type == "text":
                    color = utils.hex_to_rgb(args.color)
                    watermark_pdf_by_text(doc_path=args.input_path, wm_text=args.mark_text, page_range=args.page_range, layer=args.layer, output_path=args.output, font=args.font_family, fontsize=args.font_size, angle=args.angle, text_stroke_color_rgb=(0, 0, 0), text_fill_color_rgb=color, text_fill_alpha=args.opacity, num_lines=args.num_lines, line_spacing=args.line_spacing, word_spacing=args.word_spacing, multiple_mode=args.multiple_mode, x_offset=args.x_offset, y_offset=args.y_offset)
                elif args.type == "image":
                    watermark_pdf_by_image(doc_path=args.input_path, wm_path=args.wm_path, page_range=args.page_range, layer=args.layer,  output_path=args.output, scale=args.scale, angle=args.angle, opacity=args.opacity, multiple_mode=args.multiple_mode, num_lines=args.num_lines, line_spacing=args.line_spacing, word_spacing=args.word_spacing, x_offset=args.x_offset, y_offset=args.y_offset)
                elif args.type == "pdf":
                    watermark_pdf_by_pdf(doc_path=args.input_path, wm_doc_path=args.wm_path, page_range=args.page_range, layer=args.layer, output_path=args.output)
            elif args.watermark_which == "remove":
                if args.method == "type":
                    remove_watermark_by_type(doc_path=args.input_path, page_range=args.page_range, output_path=args.output)
                elif args.method == "index":
                    remove_watermark_by_index(doc_path=args.input_path, wm_index=args.wm_index, page_range=args.page_range, output_path=args.output)
                elif args.method == "text":
                    remove_watermark_by_text(doc_path=args.input_path, wm_text=args.wm_text, output_path=args.output)
            elif args.watermark_which == "detect":
                detect_watermark_index_helper(doc_path=args.input_path, wm_page_number=args.wm_index, outpath=args.output)
        elif args.which == "mask":
            if args.type == "rect":
                mask_pdf_by_rectangle(doc_path=args.input_path, bbox_list=args.bbox, color=args.color, opacity=args.opacity, angle=args.angle, unit=args.unit, page_range=args.page_range, output_path=args.output)
            elif args.type == "annot":
                mask_pdf_by_rectangle_annot(doc_path=args.input_path, annot_page=args.annot_page, color=args.color, opacity=args.opacity, angle=args.angle, page_range=args.page_range, output_path=args.output)
        elif args.which == "bg":
            if args.type == "color":
                add_doc_background_by_color(doc_path=args.input_path, color=args.color, opacity=args.opacity, angle=args.angle, x_offset=args.x_offset, y_offset=args.y_offset, page_range=args.page_range, output_path=args.output)
            elif args.type == "image":
                add_doc_background_by_image(doc_path=args.input_path, img_path=args.img_path, opacity=args.opacity, angle=args.angle, x_offset=args.x_offset, y_offset=args.y_offset, scale=args.scale, page_range=args.page_range, output_path=args.output)
        elif args.which == "header_footer":
            if args.type == "add":
                content_list = [args.header_left, args.header_center, args.header_right, args.footer_left, args.footer_center, args.footer_right]
                insert_header_and_footer(doc_path=args.input_path, content_list=content_list, font_family=args.font_family, font_size=args.font_size, font_color=args.font_color, opacity=args.opacity, margin_bbox=args.margin_bbox, page_range=args.page_range, unit=args.unit, output_path=args.output)
            elif args.type == "remove":
                remove_header_and_footer(doc_path=args.input_path, margin_bbox=args.margin_bbox, remove_list=args.remove, unit=args.unit, page_range=args.page_range, output_path=args.output)
        elif args.which == "page_number":
            if args.type == "add":
                insert_page_number(doc_path=args.input_path, format=args.format, pos=args.pos, start=args.start, margin_bbox=args.margin_bbox, font_family=args.font_family, font_size=args.font_size, font_color=args.font_color, opacity=args.opacity, align=args.align, page_range=args.page_range, unit=args.unit, output_path=args.output)
            elif args.type == "remove":
                remove_page_number(doc_path=args.input_path, margin_bbox=args.margin_bbox, pos=args.pos, unit=args.unit, page_range=args.page_range, output_path=args.output)
        elif args.which == "dual":
            if args.input_path.lower().endswith(".pdf"):
                make_dual_layer_pdf(input_path=args.input_path, dpi=args.dpi, page_range=args.page_range, lang=args.lang, output_path=args.output)
            elif args.input_path.lower().endswith(".png") or args.input_path.lower().endswith(".jpg") or args.input_path.lower().endswith(".jpeg"):
                make_dual_layer_pdf_from_image(doc_path=args.input_path, lang=args.lang, output_path=args.output)
            else:
                raise ValueError("不支持的文件类型!")
        elif args.which == "sign":
            sign_img(img_path=args.input_path, output_path=args.output)
        elif args.which == "annot":
            if args.method == "remove":
                delete_annot_pdf(doc_path=args.input_path, annot_types=args.annot_types, page_range=args.page_range, output_path=args.output)
    except:
        logger.error(traceback.format_exc())
        parser.print_help()
        sys.exit(1)
