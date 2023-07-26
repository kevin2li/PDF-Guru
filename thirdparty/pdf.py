import utils
from background import add_doc_background_by_color, add_doc_background_by_image
from bookmark import (add_toc_by_gap, add_toc_from_file, extract_toc,
                      find_title_by_rect_annot, transform_toc_file)
from cmd_parser import getParser
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

logger.add(logpath, rotation="1 week", retention="10 days", level="DEBUG", encoding="utf-8")

def main():
    parser = getParser()
    args = parser.parse_args()
    logger.debug(args)
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

if __name__ == "__main__":
    main()