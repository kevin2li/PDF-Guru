import { message, Modal } from 'ant-design-vue';

interface MergeState {
    input_path_list: string[];
    output: string;
    sort: string;
    sort_direction: string;
}

interface SplitState {
    input: string;
    output: string;
    page: string;
    op: string;
    span: number;
    bookmark_level: string;
}

interface InsertState {
    input: string;
    output: string;
    page: string;
    op: string;
    insert_type: string;
    paper_size: string;
    orientation: string;
    count: number;
    src_pos_type: string;
    src_pos: number;
    src_path: string;
    dst_path: string;
    src_range: string;
    dst_range: string;
}

interface CropState {
    input: string;
    output: string;
    page: string;
    op: string;
    unit: string;
    keep_size: boolean;
    up: number;
    left: number;
    down: number;
    right: number;
}

interface CutState {
    input: string;
    output: string;
    page: string;
    op: string;
    split_h_breakpoints: number[];
    split_v_breakpoints: number[];
    split_type: string;
    rows: number;
    cols: number;
    orientation: string;
    paper_size: string;
}

interface ExtractState {
    input: string;
    output: string;
    page: string;
    op: string;
}

interface EncryptState {
    input: string;
    output: string;
    op: string;
    upw: string;
    opw: string;
    perm: string[];
    is_set_upw: boolean;
    is_set_opw: boolean;
    upw_confirm: string;
    opw_confirm: string;
}

interface WatermarkState {
    input: string;
    output: string;
    page: string;
    op: string;
    type: string;
    text: string;
    font_family: string;
    font_size: number;
    font_color: string;
    font_opacity: number;
    num_lines: number;
    word_spacing: number;
    line_spacing: number;
    x_offset: number;
    y_offset: number;
    multiple_mode: boolean;
    rotate: number;
    lines: number;
    remove_method: string;
    step: string;
    wm_index: string;
    wm_path: string;
    scale: number;
    mask_type: string;
    unit: string;
    width: number;
    height: number;
    annot_page: number;
    mask_color: string;
    mask_opacity: number;
    layer: string;
}

interface ConvertState {
    input: string;
    output: string;
    page: string;
    type: string;
    dpi: number;
    is_merge: boolean;
}
interface CompressState {
    input: string;
    output: string;
}

interface RotateState {
    input: string;
    output: string;
    page: string;
    degree: number;
}

interface BookmarkState {
    input: string;
    output: string;
    page: string;
    op: string;
    extract_format: string;
    bookmark_file: string;
    write_type: string;
    write_format: string;
    write_offset: number;
    write_gap: number;
    transform_offset: number;
    transform_indent: boolean;
    transform_dots: boolean;
    ocr_lang: string;
    ocr_double_column: boolean;
    delete_level_below: number;
    default_level: number;
    remove_blank_lines: boolean;
    recognize_type: string;
}

interface OcrState {
    input: string;
    output: string;
    page: string;
    lang: string;
    double_column: boolean;
    engine: string;
}

interface DeleteState {
    input: string;
    output: string;
    page: string;
}
interface ReorderState {
    input: string;
    output: string;
    page: string;
}
interface ScaleState {
    input: string;
    output: string;
    page: string;
    op: string;
    ratio: number;
    paper_size: string;
    width: number;
    height: number;
    unit: string;
}

interface PreferencesState {
    pdf_path: string;
    python_path: string;
    tesseract_path: string;
    pandoc_path: string;
    hashcat_path: string;
    allow_modify: boolean;
}

interface FormState {
    merge: MergeState;
    split: SplitState;
    insert: InsertState;
    crop: CropState;
    extract: ExtractState;
    encrypt: EncryptState;
    convert: ConvertState;
    watermark: WatermarkState;
    scale: ScaleState;
    rotate: RotateState;
    bookmark: BookmarkState;
    ocr: OcrState;
    page: string;
    input: string;
    output: string;
}

interface BackgroundState {
    input: string;
    output: string;
    page: string;
    op: string;
    color: string;
    image_path: string;
    opacity: number;
    scale: number;
    x_offset: number;
    y_offset: number;
    degree: number;
}

interface HeaderAndFooterState {
    input: string;
    output: string;
    page: string;
    op: string;
    is_set_header: boolean;
    is_set_footer: boolean;
    header_left: string;
    header_center: string;
    header_right: string;
    footer_left: string;
    footer_center: string;
    footer_right: string;
    font_family: string;
    font_size: number;
    font_color: string;
    opacity: number;
    up: number;
    left: number;
    down: number;
    right: number;
    unit: string;
    remove_list: string[];
}

interface PageNumberState {
    input: string;
    output: string;
    page: string;
    op: string;
    pos: string;
    number_style: string;
    number_start: number;
    custom_style: string;
    is_custom_style: boolean;
    align: string;
    font_family: string;
    font_size: number;
    font_color: string;
    opacity: number;
    up: number;
    left: number;
    down: number;
    right: number;
    unit: string;
}

interface DualLayerState {
    input: string;
    output: string;
    page: string;
    dpi: number;
    lang: string;
}
interface CrackState {
    input: string;
    output: string;
    crack_type: string;
    hash_type: string;
    charset: string;
    attack_mode: string;
    dict_path: string;
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
    "crop": "PDF裁剪",
    "cut": "PDF分割/组合",
    "header": "页眉页脚",
    "background": "文档背景",
    "page_number": "页码设置",
    "extract": "PDF提取",
    "compress": "PDF压缩",
    "convert": "PDF转换",
    "encrypt": "PDF加解密",
    "ocr": "OCR识别",
    "meta": "查看元信息",
    "dual": "双层PDF制作",
    "crack": "密码破解",
    "settings": "首选项"
};

const menuDesc: Record<string, string> = {
    "merge": "将多个PDF文件合并为一个PDF文件,路径支持使用通配符'*'",
    "split": "将原始PDF文件按照给定的块大小进行分割",
    "cut": "将原始页面分割成多个页面,或将多个页面组合为一个页面",
    "delete": "将原始PDF文件中的指定页面删除",
    "reorder": "根据指定的页码范围重新调整页面顺序",
    "insert": "插入或替换PDF文件的指定页面",
    "bookmark": "从原始PDF文件中提取书签信息，或将PDF书签信息写入PDF文件",
    "watermark": "将原始PDF文件按照给定的水印参数添加水印,或者将原始PDF文件中的水印去除",
    "header": "设置页眉页脚，支持设置字体、字号、颜色、位置等属性",
    "background": "添加文档背景，支持颜色、图片等多种背景类型",
    "page_number": "页码设置，支持多种页码样式",
    "scale": "将原始PDF文件按照给定的缩放参数进行缩放",
    "rotate": "将原始PDF文件按照给定的旋转角度进行旋转",
    "crop": "将原始PDF文件(的指定页面)按照给定参数进行裁剪或分割",
    "extract": "从原始PDF文件中提取指定的内容，包括页面、文本、图片、表格等",
    "compress": "通过去除内嵌字体和图片等多余的页面资源来优化原始PDF文件以最大化PDF压缩",
    "convert": "PDF转换，支持将PDF文件转换为png、svg、docx等多种格式，或将其他格式文件转换为PDF文件",
    "encrypt": "对PDF文件进行加密或解密",
    "ocr": "对PDF文件或图片(支持png、jpg格式)进行OCR识别",
    "meta": "查看文档属性",
    "dual": "双层PDF制作，可以为扫描件创建隐藏文字图层，从而支持文字复制、检索等功能",
    "crack": "密码破解",
    "settings": "对软件功能进行配置"
}

async function handleOps(func: any, args: any[]) {
    await func(...args).then((res: any) => {
        console.log({ res });
        if (!res) {
            message.success('处理成功！');
        } else {
            message.error('处理失败！');
        }
    }).catch((err: any) => {
        console.log({ err });
        Modal.error({
            title: '处理失败！',
            content: err,
        });
    });
}

export { menuRecord, menuDesc, handleOps };
export type {
    FormState,
    InsertState,
    MergeState,
    SplitState,
    DeleteState,
    CompressState,
    ReorderState,
    CropState,
    CutState,
    ExtractState,
    EncryptState,
    WatermarkState,
    ConvertState,
    RotateState,
    BookmarkState,
    OcrState,
    ScaleState,
    PreferencesState,
    BackgroundState,
    HeaderAndFooterState,
    PageNumberState,
    DualLayerState,
    CrackState,
};
