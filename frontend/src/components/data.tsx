interface FormState {
    merge: {
        path_list: string[];
        sort: string;
        sort_direction: string;
    };
    split: {
        op: string;
        span: number;
        ranges: string;
        bookmark_level: string;
    };
    insert: {
        op: string;
        src_pos: number;
        src_path: string;
        dst_path: string;
        src_range: string;
        dst_range: string;
    };
    crop: {
        op: string;
        unit: string;
        up: number;
        left: number;
        down: number;
        right: number;
        split_h_breakpoints: number[];
        split_v_breakpoints: number[];
        split_type: string;
        split_rows: number;
        split_cols: number;
    };
    extract: {
        op: string;
    };
    encrypt: {
        op: string;
        upw: string;
        opw: string;
        perm: string[];
        is_set_upw: boolean;
        is_set_opw: boolean;
        upw_confirm: string;
        opw_confirm: string;
    };
    convert: {
        type: string;
    };
    watermark: {
        op: string;
        type: string;
        text: string;
        font_family: string;
        font_size: number;
        font_color: string;
        font_opacity: number;
        quaility: number;
        rotate: number;
        space: number;
    };
    scale: {
        scale_conf: string;
    };
    rotate: {
        op: string;
        degree: number;
        flip_method: string;
    };
    bookmark: {
        op: string;
        file: string;
        write_type: string;
        write_format: string;
        write_offset: number;
        write_gap: number;
        extract_format: string;
        transform_offset: number;
        transform_indent: boolean;
        transform_dots: boolean;
        ocr_lang: string;
        ocr_double_column: boolean;
    };
    ocr: {
        lang: string;
        double_column: boolean;
    };
    page: string;
    input: string;
    output: string;
}

const menuRecord: Record<string, string> = {
    "merge": "PDF合并",
    "split": "PDF拆分",
    "delete": "PDF删除",
    "reorder": "PDF重排",
    "insert": "PDF插入/替换",
    "bookmark": "PDF书签",
    "watermark": "PDF水印",
    "scale": "PDF缩放",
    "rotate": "PDF旋转",
    "crop": "PDF裁剪/分割",
    "extract": "PDF提取",
    "compress": "PDF压缩",
    "convert": "PDF转换",
    "encrypt": "PDF加解密",
    "ocr": "OCR识别",
    "settings": "首选项"
};
const menuDesc: Record<string, string> = {
    "merge": "将多个PDF文件合并为一个PDF文件,路径支持使用通配符'*'",
    "split": "将原始PDF文件按照给定的块大小进行分割",
    "delete": "将原始PDF文件中的指定页面删除",
    "insert": "插入或替换PDF文件的指定页面",
    "bookmark": "从原始PDF文件中提取书签信息，或将PDF书签信息写入PDF文件",
    "watermark": "将原始PDF文件按照给定的水印参数添加水印",
    "scale": "将原始PDF文件按照给定的缩放参数进行缩放",
    "rotate": "将原始PDF文件按照给定的旋转角度进行旋转",
    "crop": "将原始PDF文件(的指定页面)按照给定参数进行裁剪或分割",
    "extract": "从原始PDF文件中提取指定的内容，包括页面、文本、图片、表格等",
    "compress": "通过去除内嵌字体和图片等多余的页面资源来优化原始PDF文件以最大化PDF压缩",
    "convert": "PDF转换",
    "encrypt": "对PDF文件进行加密或解密",
    "ocr": "对PDF文件或图片(支持png、jpg格式)进行OCR识别",
    "settings": "首选项"
}

export { menuRecord, menuDesc };
export type { FormState };
