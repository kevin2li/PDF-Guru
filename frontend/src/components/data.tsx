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
    up: number;
    left: number;
    down: number;
    right: number;
    split_h_breakpoints: number[];
    split_v_breakpoints: number[];
    split_type: string;
    split_rows: number;
    split_cols: number;
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
    quaility: number;
    rotate: number;
    space: number;
}

interface ConvertState {
    input: string;
    output: string;
    page: string;
    type: string;
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
}

interface OcrState {
    input: string;
    output: string;
    page: string;
    lang: string;
    double_column: boolean;
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
    scale_conf: string;
}

interface PreferencesState {
    ocr_path: string;
    pandoc_path: string;
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
    "reorder": "根据指定的页码范围重新调整页面顺序",
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
export type { FormState, InsertState, MergeState, SplitState, DeleteState, CompressState, ReorderState, CropState, ExtractState, EncryptState, WatermarkState, ConvertState, RotateState, BookmarkState, OcrState, ScaleState, PreferencesState };
