<template>
    <a-row>
        <a-col :span="4">
            <a-menu v-model:selectedKeys="currentMenu" style="width: 180px" mode="inline">
                <a-menu-item key="merge">
                    <template #icon>
                        <block-outlined />
                    </template>
                    {{ menuRecord['merge'] }}
                </a-menu-item>
                <a-menu-item key="split">
                    <template #icon>
                        <borderless-table-outlined />
                    </template>
                    {{ menuRecord['split'] }}
                </a-menu-item>
                <a-menu-item key="delete">
                    <template #icon>
                        <close-outlined />
                    </template>
                    {{ menuRecord['delete'] }}
                </a-menu-item>
                <a-menu-item key="reorder">
                    <template #icon>
                        <ordered-list-outlined />
                    </template>
                    {{ menuRecord['reorder'] }}
                </a-menu-item>
                <a-menu-item key="bookmark">
                    <template #icon>
                        <bars-outlined />
                    </template>
                    {{ menuRecord['bookmark'] }}
                </a-menu-item>
                <a-menu-item key="scale">
                    <template #icon>
                        <fullscreen-outlined />
                    </template>
                    {{ menuRecord['scale'] }}
                </a-menu-item>
                <a-menu-item key="watermark">
                    <template #icon>
                        <highlight-outlined />
                    </template>
                    {{ menuRecord['watermark'] }}
                </a-menu-item>
                <a-menu-item key="rotate">
                    <template #icon>
                        <rotate-right-outlined />
                    </template>
                    {{ menuRecord['rotate'] }}
                </a-menu-item>
                <a-menu-item key="crop">
                    <template #icon>
                        <scissor-outlined />
                    </template>
                    {{ menuRecord['crop'] }}
                </a-menu-item>
                <a-menu-item key="extract">
                    <template #icon>
                        <aim-outlined />
                    </template>
                    {{ menuRecord['extract'] }}
                </a-menu-item>
                <a-menu-item key="compress">
                    <template #icon>
                        <file-zip-outlined />
                    </template>
                    {{ menuRecord['compress'] }}
                </a-menu-item>
                <a-menu-item key="convert">
                    <template #icon>
                        <export-outlined />
                    </template>
                    {{ menuRecord['convert'] }}

                </a-menu-item>
                <a-menu-item key="encrypt">
                    <template #icon>
                        <lock-outlined />
                    </template>
                    {{ menuRecord['encrypt'] }}

                </a-menu-item>
                <a-menu-item key="settings">
                    <template #icon>
                        <SettingOutlined />
                    </template>
                    {{ menuRecord['settings'] }}
                </a-menu-item>

            </a-menu>
        </a-col>
        <a-col :span="20">
            <div>
                <!-- <h1>{{ text }}</h1>
                <a-button type="primary" @click="hello">Greet</a-button> -->
                <div style="margin-right: 5vw;margin-top: 0.5em;">
                    <a-typography-title>{{ menuRecord[currentMenu.at(0) || "merge"] }}</a-typography-title>
                    <a-typography-paragraph>
                        <blockquote>功能说明：{{ menuDesc[currentMenu.at(0) || "merge"] }}</blockquote>
                    </a-typography-paragraph>
                </div>
                <div>
                    <a-form name="customized_form_controls"
                        style="border: 1px solid #dddddd; padding: 10px 0;border-radius: 10px;margin-right: 5vw;"
                        :model="formState" :label-col="{ span: 3 }" :wrapper-col="{ offset: 1, span: 18 }">
                        <!-- PDF分割 -->
                        <a-form-item name="span" label="批大小" v-if="currentMenu.at(0) == 'split'">
                            <a-input-number v-model:value="formState.span" :min="1" />
                        </a-form-item>
                        <a-form-item name="split_mode" label="模式" v-if="currentMenu.at(0) == 'split'">
                            <a-radio-group v-model:value="formState.split_mode">
                                <a-radio value="span">span</a-radio>
                                <a-radio value="bookmark">bookmark</a-radio>
                            </a-radio-group>
                        </a-form-item>

                        <!-- PDF合并 -->


                        <!-- PDF旋转 -->
                        <a-form-item name="rotate" label="旋转角度" v-if="currentMenu.at(0) == 'rotate'">
                            <a-radio-group v-model:value="formState.rotate">
                                <a-radio :value="90">顺时针90</a-radio>
                                <a-radio :value="180">顺时针180</a-radio>
                                <a-radio :value="270">逆时针90</a-radio>
                            </a-radio-group>
                        </a-form-item>

                        <!-- PDF书签 -->
                        <a-form-item name="bookmark_op" label="类型" v-if="currentMenu.at(0) == 'bookmark'">
                            <a-radio-group button-style="solid" v-model:value="formState.bookmark_op">
                                <a-radio-button value="extract">提取书签</a-radio-button>
                                <a-radio-button value="write">写入书签</a-radio-button>
                                <a-radio-button value="transform">转换书签</a-radio-button>
                            </a-radio-group>
                        </a-form-item>
                        <a-form-item name="bookmark_input" label="书签文件" :rules="{ required: true }"
                            v-if="currentMenu.at(0) == 'bookmark' && formState.bookmark_op == 'write'">
                            <a-input v-model:value="formState.bookmark_input" placeholder="书签文件路径" />
                        </a-form-item>
                        <a-form-item name="bookmark_transform_offset" label="页码偏移量" :rules="{ required: true }"
                            v-if="currentMenu.at(0) == 'bookmark' && formState.bookmark_op == 'transform'">
                            <a-input-number v-model:value="formState.bookmark_transform_offset" placeholder="页码偏移量" />
                        </a-form-item>
                        <a-form-item name="bookmark_transform_indent" label="增加缩进" :rules="{ required: true }"
                            v-if="currentMenu.at(0) == 'bookmark' && formState.bookmark_op == 'transform'">
                            <a-switch v-model:checked="formState.bookmark_transform_indent" />
                        </a-form-item>
                        <a-form-item name="bookmark_transform_dots" label="删除尾部点" :rules="{ required: true }"
                            v-if="currentMenu.at(0) == 'bookmark' && formState.bookmark_op == 'transform'">
                            <a-switch v-model:checked="formState.bookmark_transform_dots" />
                        </a-form-item>
                        <a-form-item name="bookmark_extract_format" label="类型"
                            v-if="currentMenu.at(0) == 'bookmark' && formState.bookmark_op == 'extract'">
                            <a-select v-model:value="formState.bookmark_extract_format" style="width: 200px">
                                <a-select-option value="txt">txt</a-select-option>
                                <a-select-option value="json">json</a-select-option>
                            </a-select>
                        </a-form-item>

                        <!-- PDF提取 -->
                        <a-form-item name="extract_op" label="提取类型" v-if="currentMenu.at(0) == 'extract'">
                            <a-radio-group button-style="solid" v-model:value="formState.extract_op">
                                <a-radio-button value="text">文本</a-radio-button>
                                <a-radio-button value="image">图片</a-radio-button>
                                <a-radio-button value="table">表格</a-radio-button>
                            </a-radio-group>
                        </a-form-item>
                        <!-- PDF缩放 -->
                        <a-form-item name="scale_conf" label="缩放参数" v-if="currentMenu.at(0) == 'scale'">
                            <a-input v-model:value="formState.scale_conf" placeholder="缩放参数" />
                        </a-form-item>
                        <!-- PDF转换 -->
                        <a-form-item name="convert_dest_format" label="目标格式" v-if="currentMenu.at(0) == 'convert'">
                            <a-select v-model:value="formState.convert_dest_format" style="width: 200px">
                                <a-select-opt-group label="PDF转其他">
                                    <a-select-option value="pdf2png">pdf转png</a-select-option>
                                    <a-select-option value="pdf2svg">pdf转svg</a-select-option>
                                    <a-select-option value="pdf2html">pdf转html</a-select-option>
                                    <a-select-option value="pdf2word">pdf转word</a-select-option>
                                </a-select-opt-group>
                                <a-select-opt-group label="其他转PDF">
                                    <a-select-option value="png2pdf">png转pdf</a-select-option>
                                    <a-select-option value="svg2pdf">svg转pdf</a-select-option>
                                    <a-select-option value="word2pdf">word转pdf</a-select-option>
                                </a-select-opt-group>
                            </a-select>
                        </a-form-item>
                        <!-- PDF加解密 -->
                        <a-form-item name="encrypt_op" label="类型" v-if="currentMenu.at(0) == 'encrypt'">
                            <a-radio-group button-style="solid" v-model:value="formState.encrypt_op">
                                <a-radio-button value="encrypt">加密</a-radio-button>
                                <a-radio-button value="decrypt">解密</a-radio-button>
                            </a-radio-group>
                        </a-form-item>
                        <a-form-item name="encrypt_mode" label="算法" v-if="false">
                            <a-radio-group v-model:value="formState.encrypt_mode">
                                <a-radio value="RC4">RC4</a-radio>
                                <a-radio value="AES">AES</a-radio>
                            </a-radio-group>
                        </a-form-item>
                        <a-form-item name="encrypt_key" label="密钥长度" v-if="false">
                            <a-radio-group v-model:value="formState.encrypt_key">
                                <a-radio :value="40">40</a-radio>
                                <a-radio :value="128">128</a-radio>
                                <a-radio :value="256" v-if="formState.encrypt_mode == 'AES'">256</a-radio>
                            </a-radio-group>
                        </a-form-item>
                        <a-form-item name="encrypt_opw" label="所有者密码" v-if="false">
                            <a-input v-model:value="formState.encrypt_opw" placeholder="所有者密码" />
                        </a-form-item>
                        <a-form-item name="encrypt_upw" label="设置密码" :rules="{ required: true }"
                            v-if="currentMenu.at(0) == 'encrypt'">
                            <a-input-password v-model:value="formState.encrypt_upw" placeholder="不少于6位" />
                        </a-form-item>
                        <a-form-item name="encrypt_upw_confirm" label="确认密码" :rules="{ required: true }"
                            v-if="currentMenu.at(0) == 'encrypt' && formState.encrypt_op == 'encrypt'">
                            <a-input-password v-model:value="formState.encrypt_upw_confirm" placeholder="再次输入密码" />
                        </a-form-item>
                        <a-form-item name="encrypt_perm" label="限制功能"
                            v-if="currentMenu.at(0) == 'encrypt' && formState.encrypt_op == 'encrypt'">
                            <a-checkbox v-model:checked="checkAll" :indeterminate="indeterminate"
                                @change="onCheckAllChange">全选</a-checkbox>
                            <a-divider type="vertical" />
                            <a-checkbox-group v-model:value="formState.encrypt_perm" :options="encrypt_perm_options" />
                        </a-form-item>
                        <!-- PDF水印 -->
                        <a-form-item name="watermark_op" label="水印类型" v-if="currentMenu.at(0) == 'watermark'">
                            <a-radio-group button-style="solid" v-model:value="formState.watermark_op">
                                <a-radio-button value="text">文本</a-radio-button>
                                <a-radio-button value="image" disabled>图片</a-radio-button>
                            </a-radio-group>
                        </a-form-item>
                        <a-form-item name="watermark_font_family" label="字体" v-if="currentMenu.at(0) == 'watermark'">
                            <a-select v-model:value="formState.watermark_font_family" style="width: 200px">
                                <a-select-option value="微软雅黑">微软雅黑</a-select-option>
                                <a-select-option value="宋体">宋体</a-select-option>
                                <a-select-option value="黑体">黑体</a-select-option>
                                <a-select-option value="楷体">楷体</a-select-option>
                                <a-select-option value="仿宋">仿宋</a-select-option>
                                <a-select-option value="幼圆">幼圆</a-select-option>
                                <a-select-option value="华文琥珀">华文琥珀</a-select-option>
                                <a-select-option value="方正舒体">方正舒体</a-select-option>
                                <a-select-option value="Arial">Arial</a-select-option>
                                <a-select-option value="TimesNewRoman">TimesNewRoman</a-select-option>
                            </a-select>
                        </a-form-item>
                        <a-form-item name="watermark_font_size" label="字号" v-if="currentMenu.at(0) == 'watermark'">
                            <a-input-number v-model:value="formState.watermark_font_size" :min="1" />
                        </a-form-item>
                        <a-form-item name="watermark_font_color" label="颜色" v-if="currentMenu.at(0) == 'watermark'">
                            <a-input v-model:value="formState.watermark_font_color" placeholder="字体颜色" />
                        </a-form-item>
                        <a-form-item name="watermark_font_opacity" label="不透明度" v-if="currentMenu.at(0) == 'watermark'">
                            <a-input-number v-model:value="formState.watermark_font_opacity" :min="0" :max="1"
                                :step="0.01" />
                        </a-form-item>
                        <a-form-item name="watermark_rotate" label="旋转角度" v-if="currentMenu.at(0) == 'watermark'">
                            <a-input-number v-model:value="formState.watermark_rotate" :min="0" :max="360" />
                        </a-form-item>
                        <a-form-item name="watermark_space" label="文字间距" v-if="currentMenu.at(0) == 'watermark'">
                            <a-input-number v-model:value="formState.watermark_space" :min="0" :max="360" />
                        </a-form-item>

                        <!-- 通用 -->
                        <a-form-item name="page" label="页码范围"
                            v-if="['rotate', 'reorder', 'watermark', 'crop', 'extract', 'convert', 'scale', 'delete'].includes(currentMenu.at(0) || '')">
                            <a-input v-model:value="formState.page" placeholder="页码范围, e.g. 1-3,9-10" />
                        </a-form-item>
                        <a-form-item name="input" label="输入" :rules="[{ required: true, message: '请输入路径!' }]">
                            <a-input v-model:value="formState.input" placeholder="输入文件路径" />
                        </a-form-item>
                        <a-form-item name="output" label="输出">
                            <a-input v-model:value="formState.output" placeholder="输出目录" />
                        </a-form-item>
                        <a-form-item :wrapperCol="{ offset: 4 }" style="margin-bottom: 10px;">
                            <a-button type="primary" html-type="submit" @click="onSubmit"
                                :loading="confirmLoading">确认</a-button>
                        </a-form-item>
                    </a-form>
                </div>
            </div>
        </a-col>
    </a-row>
</template>
<script lang="ts">
import { defineComponent, reactive, watch, ref } from 'vue';
import { MailOutlined, AppstoreOutlined, SettingOutlined, BarsOutlined, BorderlessTableOutlined, ScissorOutlined, CopyOutlined, BlockOutlined, FileZipOutlined, RotateRightOutlined, LockOutlined, OrderedListOutlined, HighlightOutlined, AimOutlined, ExportOutlined, UploadOutlined, FullscreenOutlined, CloseOutlined } from '@ant-design/icons-vue';
import { message, Modal } from 'ant-design-vue';
import { MergePDF, ScalePDF, ReorderPDF, CompressPDF, SplitPDF, RotatePDF, EncryptPDF, DecryptPDF, ConvertPDF } from '../../wailsjs/go/main/App';

export default defineComponent({
    components: {
        MailOutlined,
        AppstoreOutlined,
        SettingOutlined,
        BarsOutlined,
        BorderlessTableOutlined,
        ScissorOutlined,
        CopyOutlined,
        BlockOutlined,
        FileZipOutlined,
        RotateRightOutlined,
        LockOutlined,
        OrderedListOutlined,
        HighlightOutlined,
        AimOutlined,
        ExportOutlined,
        UploadOutlined,
        FullscreenOutlined,
        CloseOutlined
    },
    setup() {
        const menuRecord: Record<string, string> = {
            "merge": "PDF合并",
            "split": "PDF分割",
            "delete": "PDF删除",
            "reorder": "PDF重排",
            "bookmark": "PDF书签",
            "watermark": "PDF水印",
            "scale": "PDF缩放",
            "rotate": "PDF旋转",
            "crop": "PDF裁剪",
            "extract": "PDF提取",
            "compress": "PDF压缩",
            "convert": "PDF转换",
            "encrypt": "PDF加解密",
            "settings": "首选项"
        };
        const menuDesc: Record<string, string> = {
            "merge": "将多个PDF文件合并为一个PDF文件,路径支持使用通配符'*'",
            "split": "将原始PDF文件按照给定的批大小进行分割",
            "delete": "将原始PDF文件中的指定页面删除",
            "reorder": "将原始PDF文件按照给定的页码顺序进行重新排列",
            "bookmark": "从原始PDF文件中提取书签信息，或将PDF书签信息写入PDF文件",
            "watermark": "将原始PDF文件按照给定的水印参数添加水印",
            "scale": "将原始PDF文件按照给定的缩放参数进行缩放",
            "rotate": "将原始PDF文件按照给定的旋转角度进行旋转",
            "crop": "将原始PDF文件(的指定页面)按照给定的裁剪参数进行裁剪",
            "extract": "从原始PDF文件中提取指定的内容，包括文本、图片、表格等",
            "compress": "通过去除内嵌字体和图片等多余的页面资源来优化原始PDF文件以最大化PDF压缩",
            "convert": "PDF转换",
            "encrypt": "对PDF文件进行加密或解密",
            "settings": "首选项"
        }
        const encrypt_perm_options = [
            "复制", "注释", "打印", "表单", "插入/删除页面"
        ];
        const confirmLoading = ref<boolean>(false);
        const indeterminate = ref<boolean>(false);
        const checkAll = ref<boolean>(false);
        const formState = reactive({
            page: "",
            split_mode: "span",
            bookmark_op: "extract",
            extract_op: "text",
            encrypt_op: "encrypt",
            encrypt_mode: "AES",
            encrypt_key: 256,
            encrypt_perm: ["打开"],
            encrypt_upw: "",
            encrypt_opw: "",
            encrypt_upw_confirm: "",
            convert_dest_format: "png",
            watermark_op: "text",
            watermark_font_family: "微软雅黑",
            watermark_font_size: 14,
            watermark_font_color: "#808080",
            watermark_font_opacity: 0.15,
            watermark_rotate: 30,
            watermark_space: 75,
            scale_conf: "",
            rotate: 90,
            span: 5,
            bookmark_input: "",
            bookmark_extract_format: "txt",
            bookmark_transform_offset: 0,
            bookmark_transform_indent: false,
            bookmark_transform_dots: false,
            input: "",
            output: ""
        });
        const onSubmit = async () => {
            console.log(formState);
            confirmLoading.value = true;
            switch (currentMenu.value.at(0)) {
                case "split": {
                    await SplitPDF(formState.input, formState.split_mode, formState.span, formState.output).then((res: any) => {
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
                    })
                    break;
                }
                case "merge": {
                    const inFiles = formState.input.split(";").map((item: string) => item.trim());
                    await MergePDF(inFiles, formState.output, "create", false).then((res: any) => {
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
                    })
                    break;
                }
                case "reorder": {
                    await ReorderPDF(formState.input, formState.output, formState.page).then((res: any) => {
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
                    })
                    break;
                }
                case "bookmark": {

                    break;
                }
                case "watermark": {
                    break;
                }
                case "rotate": {
                    await RotatePDF(formState.input, formState.output, formState.rotate, formState.page).then((res: any) => {
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
                    })
                    break;
                }
                case "crop": {
                    break;
                }
                case "delete": {
                    let pageStr = formState.page.split(",").map(item => {
                        return "!" + item.trim();
                    }).join(",");
                    await ReorderPDF(formState.input, formState.output, pageStr).then((res: any) => {
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
                    })
                    break;
                }
                case "extract": {
                    break;
                }
                case "compress": {
                    await CompressPDF(formState.input, formState.output).then((res: any) => {
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
                    })
                    break;
                }
                case "convert": {
                    await ConvertPDF(formState.input, formState.output, formState.convert_dest_format, formState.page).then((res: any) => {
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
                    })
                    break;
                }
                case "scale": {
                    await ScalePDF(formState.input, formState.output, formState.scale_conf, formState.page).then((res: any) => {
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
                    })
                    break;
                }
                case "encrypt": {
                    if (formState.encrypt_op == "encrypt") {
                        // await EncryptPDF(formState.input, formState.output, formState.encrypt_mode, formState.encrypt_upw, formState.encrypt_opw, formState.encrypt_key, formState.encrypt_perm).then((res: any) => {
                        //     console.log({ res });
                        //     if (!res) {
                        //         message.success('处理成功！');
                        //     } else {
                        //         message.error('处理失败！');
                        //     }
                        // }).catch((err: any) => {
                        //     console.log({ err });
                        //     Modal.error({
                        //         title: '处理失败！',
                        //         content: err,
                        //     });
                        // })
                        console.log({ formState })
                    } else if (formState.encrypt_op == "decrypt") {
                        // await DecryptPDF(formState.input, formState.output, formState.encrypt_upw, formState.encrypt_opw).then((res: any) => {
                        //     console.log({ res });
                        //     if (!res) {
                        //         message.success('处理成功！');
                        //     } else {
                        //         message.error('处理失败！');
                        //     }
                        // }).catch((err: any) => {
                        //     console.log({ err });
                        //     Modal.error({
                        //         title: '处理失败！',
                        //         content: err,
                        //     });
                        // })
                    }
                    break;
                }
            }

            confirmLoading.value = false;
        }
        const onCheckAllChange = (e: any) => {
            Object.assign(formState, {
                encrypt_perm: e.target.checked ? encrypt_perm_options : [],
            });
            indeterminate.value = false;
        };
        watch(
            () => formState.encrypt_perm,
            (val: any) => {
                indeterminate.value = !!val.length && val.length < encrypt_perm_options.length;
                checkAll.value = val.length === encrypt_perm_options.length;
            }
        )
        const currentMenu = ref<string[]>(['merge']);

        return {
            confirmLoading,
            indeterminate,
            checkAll,
            menuRecord,
            menuDesc,
            encrypt_perm_options,
            currentMenu,
            formState,
            onSubmit,
            onCheckAllChange
        };
    },
});
</script>
<style>
.dynamic-delete-button {
    cursor: pointer;
    position: relative;
    top: 4px;
    font-size: 24px;
    color: #999;
    transition: all 0.3s;
}

.dynamic-delete-button:hover {
    color: #777;
}

.dynamic-delete-button[disabled] {
    cursor: not-allowed;
    opacity: 0.5;
}
</style>