<template>
    <div>
        <a-form ref="formRef" style="border: 1px solid #dddddd; padding: 10px 0;border-radius: 10px;margin-right: 5vw;"
            :model="formState" :label-col="{ span: 3 }" :wrapper-col="{ offset: 1, span: 18 }" :rules="rules"
            @finish="onFinish" @finishFailed="onFinishFailed">
            <a-form-item name="watermark_op" label="操作">
                <a-radio-group button-style="solid" v-model:value="formState.op">
                    <a-radio-button value="add">添加水印</a-radio-button>
                    <a-radio-button value="remove">去除水印</a-radio-button>
                </a-radio-group>
            </a-form-item>
            <div v-if="formState.op === 'add'">
                <a-form-item name="type" label="水印类型">
                    <a-radio-group v-model:value="formState.type">
                        <a-radio value="text">文本</a-radio>
                        <a-radio value="image">图片</a-radio>
                        <a-radio value="pdf">PDF</a-radio>
                    </a-radio-group>
                </a-form-item>
                <div v-if="formState.type === 'text'">
                    <a-form-item name="text" label="水印文本">
                        <a-textarea v-model:value="formState.text" placeholder="e.g. 内部资料" allow-clear />
                    </a-form-item>
                    <a-form-item name="watermark_font_size" label="字体属性" hasFeedback>
                        <a-space size="large">
                            <a-select v-model:value="formState.font_family" style="width: 200px" :options="font_options">
                            </a-select>
                            <a-tooltip>
                                <template #title>字号</template>
                                <a-input-number v-model:value="formState.font_size" :min="1">
                                    <template #prefix>
                                        <font-size-outlined />
                                    </template>
                                </a-input-number>
                            </a-tooltip>
                            <a-tooltip>
                                <template #title>字体颜色</template>
                                <a-input v-model:value="formState.font_color" placeholder="16进制字体颜色"
                                    :defaultValue="formState.font_color" allow-clear>
                                    <template #prefix>
                                        <font-colors-outlined />
                                    </template>
                                </a-input>
                            </a-tooltip>
                            <a
                                :style="{ background: formState.font_color, border: '1px solid black', marginLeft: '-15px' }">&nbsp;&nbsp;&nbsp;&nbsp;</a>
                        </a-space>
                    </a-form-item>
                    <a-form-item name="watermark_font_opacity" label="水印属性">
                        <a-space size="large">
                            <a-input-number v-model:value="formState.font_opacity" :min="0" :max="1" :step="0.01">
                                <template #addonBefore>
                                    不透明度
                                </template>
                            </a-input-number>
                            <a-input-number v-model:value="formState.rotate" :min="0" :max="360">
                                <template #addonBefore>
                                    旋转角度
                                </template>
                            </a-input-number>
                        </a-space>
                    </a-form-item>
                    <a-form-item label="位置">
                        <a-space size="large">
                            <a-input-number v-model:value="formState.x_offset">
                                <template #addonBefore>
                                    水平偏移量
                                </template>
                            </a-input-number>
                            <a-input-number v-model:value="formState.y_offset">
                                <template #addonBefore>
                                    垂直偏移量
                                </template>
                            </a-input-number>
                        </a-space>
                    </a-form-item>
                </div>
                <div v-if="formState.type === 'image'">
                    <a-form-item name="wm_path" hasFeedback label="水印图片路径">
                        <a-input v-model:value="formState.wm_path" placeholder="水印图片路径" allow-clear />
                    </a-form-item>
                    <a-form-item name="watermark_font_opacity" label="水印属性">
                        <a-space size="large">
                            <a-input-number v-model:value="formState.font_opacity" :min="0" :max="1" :step="0.01">
                                <template #addonBefore>
                                    不透明度
                                </template>
                            </a-input-number>
                            <a-input-number v-model:value="formState.rotate" :min="0" :max="360">
                                <template #addonBefore>
                                    旋转角度
                                </template>
                            </a-input-number>
                        </a-space>
                    </a-form-item>
                    <a-form-item label="位置和大小">
                        <a-space size="large">
                            <a-input-number v-model:value="formState.x_offset">
                                <template #addonBefore>
                                    水平偏移量
                                </template>
                            </a-input-number>
                            <a-input-number v-model:value="formState.y_offset">
                                <template #addonBefore>
                                    垂直偏移量
                                </template>
                            </a-input-number>
                            <a-input-number v-model:value="formState.scale" :min="0">
                                <template #addonBefore>
                                    缩放比例
                                </template>
                            </a-input-number>
                        </a-space>
                    </a-form-item>
                </div>
                <div v-if="formState.type === 'text' || formState.type === 'image'">
                    <a-form-item label="排布">
                        <a-radio-group v-model:value="formState.multiple_mode">
                            <a-radio :value="false">单行</a-radio>
                            <a-radio :value="true">多行</a-radio>
                        </a-radio-group>
                    </a-form-item>
                    <a-form-item label="多行水印" v-if="formState.multiple_mode">
                        <a-space size="large">
                            <a-input-number v-model:value="formState.num_lines" :min="1">
                                <template #addonBefore>
                                    行数
                                </template>
                            </a-input-number>
                            <a-input-number v-model:value="formState.line_spacing" :min="0" :max="100">
                                <template #addonBefore>
                                    行间距
                                </template>
                            </a-input-number>
                            <a-input-number v-model:value="formState.word_spacing" :min="0" :max="100">
                                <template #addonBefore>
                                    相邻水印间距
                                </template>
                            </a-input-number>
                        </a-space>
                    </a-form-item>
                </div>
                <div v-if="formState.type === 'pdf'">
                    <a-form-item name="wm_path" hasFeedback label="水印PDF路径">
                        <a-input v-model:value="formState.wm_path" placeholder="水印PDF路径" allow-clear />
                    </a-form-item>
                </div>
                <a-form-item label="层级">
                    <a-select v-model:value="formState.layer" style="width: 200px">
                        <a-select-option value="bottom">置于底层</a-select-option>
                        <a-select-option value="top">置于顶层</a-select-option>
                    </a-select>
                </a-form-item>
                <a-form-item name="page" hasFeedback :validateStatus="validateStatus.page" :help="validateHelp.page"
                    label="页码范围">
                    <a-input v-model:value="formState.page" placeholder="应用的页码范围(留空表示全部), e.g. 1-10" allow-clear />
                </a-form-item>
            </div>
            <div v-if="formState.op === 'remove'">
                <a-form-item name="remove_method" label="去水印方法">
                    <a-radio-group v-model:value="formState.remove_method">
                        <a-radio value="type">类型水印</a-radio>
                        <a-radio value="mask">遮罩水印</a-radio>
                        <a-radio value="index">内容水印</a-radio>
                    </a-radio-group>
                </a-form-item>
                <div v-if="formState.remove_method === 'type'">
                    <a-form-item name="page" hasFeedback :validateStatus="validateStatus.page" :help="validateHelp.page"
                        label="页码范围">
                        <a-input v-model:value="formState.page" placeholder="应用的页码范围(留空表示全部), e.g. 1-10" allow-clear />
                    </a-form-item>
                </div>
                <div v-if="formState.remove_method === 'index'">
                    <a-form-item name="step" label="步骤">
                        <a-radio-group v-model:value="formState.step">
                            <a-radio style="display: flex;height:30px;lineHeight:30px;" value="1">步骤一：识别水印索引</a-radio>
                            <a-radio style="display: flex;height:30px;lineHeight:30px;" value="2">步骤二：删除水印</a-radio>
                        </a-radio-group>
                    </a-form-item>
                    <a-form-item name="wm_index" label="含水印页码" v-if="formState.step === '1'">
                        <a-input v-model:value="formState.wm_index" placeholder="包含水印的页码，1页即可"></a-input>
                    </a-form-item>
                    <a-form-item name="wm_index" label="水印索引" v-if="formState.step === '2'"
                        :rules="[{ required: true, message: '请提供水印索引' }]">
                        <a-input v-model:value="formState.wm_index" placeholder="多个数字用英文逗号隔开,支持负数(表示倒数页) e.g. -1"></a-input>
                    </a-form-item>
                    <a-form-item name="page" hasFeedback :validateStatus="validateStatus.page" :help="validateHelp.page"
                        label="页码范围" v-if="formState.step === '2'">
                        <a-input v-model:value="formState.page" placeholder="应用的页码范围(留空表示全部), e.g. 1-10" allow-clear />
                    </a-form-item>
                </div>
                <div v-if="formState.remove_method === 'mask'">
                    <a-form-item name="type" label="遮罩类型">
                        <a-radio-group v-model:value="formState.mask_type">
                            <a-radio value="rect">手动指定矩形框</a-radio>
                            <a-radio value="annot">根据矩形注释确定</a-radio>
                        </a-radio-group>
                    </a-form-item>
                    <div v-if="formState.mask_type === 'rect'">
                        <a-form-item label="单位">
                            <a-radio-group v-model:value="formState.unit">
                                <a-radio value="pt">像素</a-radio>
                                <a-radio value="cm">厘米</a-radio>
                                <a-radio value="mm">毫米</a-radio>
                                <a-radio value="in">英寸</a-radio>
                            </a-radio-group>
                        </a-form-item>
                        <a-form-item name="rect" label="矩形框">
                            <a-space size="large">
                                <a-input-number v-model:value="formState.x_offset">
                                    <template #addonBefore>
                                        左上x
                                    </template>
                                </a-input-number>
                                <a-input-number v-model:value="formState.y_offset">
                                    <template #addonBefore>
                                        左上y
                                    </template>
                                </a-input-number>
                                <a-input-number v-model:value="formState.width">
                                    <template #addonBefore>
                                        宽度
                                    </template>
                                </a-input-number>
                                <a-input-number v-model:value="formState.height">
                                    <template #addonBefore>
                                        高度
                                    </template>
                                </a-input-number>
                            </a-space>
                        </a-form-item>

                    </div>
                    <div v-if="formState.mask_type === 'annot'">
                        <a-form-item name="annot_page" label="矩形注释页码">
                            <a-input-number v-model:value="formState.annot_page" :min="1"></a-input-number>
                        </a-form-item>
                    </div>
                    <a-form-item label="遮罩属性">
                        <a-row>
                            <a-col :span="6">
                                <a-space>
                                    <a-input v-model:value="formState.mask_color" placeholder="16进制字体颜色"
                                        :defaultValue="formState.mask_color" allow-clear>
                                        <template #addonBefore>
                                            颜色
                                        </template>
                                    </a-input>
                                    <a
                                        :style="{ background: formState.mask_color, border: '1px solid black' }">&nbsp;&nbsp;&nbsp;&nbsp;</a>
                                </a-space>
                            </a-col>
                            <a-col :span="6" style="margin-left: 1.5vw;">
                                <a-input-number v-model:value="formState.mask_opacity" :min="0" :max="1" :step="0.01">
                                    <template #addonBefore>
                                        不透明度
                                    </template>
                                </a-input-number>
                            </a-col>
                            <a-col :span="6">
                                <a-slider v-model:value="formState.mask_opacity" :min="0" :max="1" :step="0.01" />
                            </a-col>
                        </a-row>
                    </a-form-item>
                    <a-form-item name="page" hasFeedback :validateStatus="validateStatus.page" :help="validateHelp.page"
                        label="页码范围">
                        <a-input v-model:value="formState.page" placeholder="应用的页码范围(留空表示全部), e.g. 1-10" allow-clear />
                    </a-form-item>
                </div>
            </div>
            <a-form-item name="input" label="输入" :validateStatus="validateStatus.input" :help="validateHelp.input">
                <div>
                    <a-row>
                        <a-col :span="22">
                            <a-input v-model:value="formState.input" placeholder="输入文件路径, 支持使用*匹配多个文件, 如D:\test\*.pdf" allow-clear />
                        </a-col>
                        <a-col :span="1" style="margin-left: 1vw;">
                            <a-tooltip>
                                <template #title>选择文件</template>
                                <a-button @click="selectFile('input')"><ellipsis-outlined /></a-button>
                            </a-tooltip>
                        </a-col>
                    </a-row>
                </div>
            </a-form-item>
            <a-form-item name="output" label="输出">
                <div>
                    <a-row>
                        <a-col :span="22">
                            <a-input v-model:value="formState.output" placeholder="输出目录(留空则保存到输入文件同级目录)" allow-clear />
                        </a-col>
                        <a-col :span="1" style="margin-left: 1vw;">
                            <a-tooltip>
                                <template #title>选择文件</template>
                                <a-button @click="saveFile('output')"><ellipsis-outlined /></a-button>
                            </a-tooltip>
                        </a-col>
                    </a-row>
                </div>
            </a-form-item>
            <a-form-item :wrapperCol="{ offset: 4 }" style="margin-bottom: 10px;">
                <a-button type="primary" html-type="submit" :loading="confirmLoading">确认</a-button>
                <a-button style="margin-left: 10px" @click="resetFields">重置</a-button>
            </a-form-item>
        </a-form>
    </div>
</template>
<script lang="ts">
import { defineComponent, reactive, onMounted, ref } from 'vue';
import { message, Modal } from 'ant-design-vue';
import {
    SelectFile,
    SaveFile,
    CheckOS,
    CheckFileExists,
    CheckRangeFormat,
    WatermarkPDFByText,
    WatermarkPDFByImage,
    WatermarkPDFByPDF,
    RemoveWatermarkByIndex,
    RemoveWatermarkByType,
    DetectWatermarkByIndex,
    MaskPDFByAnnot,
    MaskPDFByRect
} from '../../../wailsjs/go/main/App';
import type { FormInstance } from 'ant-design-vue';
import type { Rule } from 'ant-design-vue/es/form';
import { FontSizeOutlined, FontColorsOutlined, EllipsisOutlined } from '@ant-design/icons-vue';
import type { SelectProps } from 'ant-design-vue';
import type { WatermarkState } from "../data";
import { handleOps, windows_fonts_options, mac_fonts_options } from "../data";
export default defineComponent({
    components: {
        FontSizeOutlined,
        FontColorsOutlined,
        EllipsisOutlined
    },
    setup() {
        const formRef = ref<FormInstance>();
        const formState = reactive<WatermarkState>({
            input: "",
            output: "",
            page: "",
            op: "add",
            type: "text",
            text: "",
            font_family: "msyh.ttc",
            font_size: 50,
            font_color: "#000000",
            font_opacity: 0.3,
            rotate: 45,
            num_lines: 1,
            multiple_mode: false,
            x_offset: 0,
            y_offset: 0,
            word_spacing: 1,
            line_spacing: 1,
            remove_method: "type",
            step: "1",
            wm_index: "",
            lines: 0,
            wm_path: "",
            scale: 1,
            mask_type: 'annot',
            unit: 'pt',
            width: 0,
            height: 0,
            annot_page: 1,
            mask_color: '#FFFFFF',
            mask_opacity: 1,
            layer: "bottom",
        });

        const color_picker_state = reactive({
            showcolorpicker: false,
            color: "#59c7f9",
            suckerCanvas: null,
            suckerArea: [],
            isSucking: false,
        });

        const validateStatus = reactive({
            input: "",
            page: "",
            font_color: "",
        });
        const validateHelp = reactive({
            input: "",
            page: "",
            font_color: "",
        });

        let font_options = ref<SelectProps['options']>([]);

        const setFontOptions = async () => {
            await CheckOS().then((res: any) => {
                if (res === "windows") {
                    font_options.value = windows_fonts_options;
                } else if (res === "darwin") {
                    font_options.value = mac_fonts_options;
                    formState.font_family = 'STHeiti Light.ttc';
                }
            }).catch((err: any) => {
                console.log({ err });
            })
        }
        onMounted(async () => {
            await setFontOptions();
        });

        const validateFileExists = async (_rule: Rule, value: string) => {
            validateStatus["input"] = 'validating';
            if (value === '') {
                validateStatus["input"] = 'error';
                validateHelp["input"] = "请填写路径";
                return Promise.reject();
            }
            await CheckFileExists(value).then((res: any) => {
                console.log({ res });
                if (res) {
                    validateStatus["input"] = 'error';
                    validateHelp["input"] = res;
                    return Promise.reject();
                }
                validateStatus["input"] = 'success';
                validateHelp["input"] = '';
                return Promise.resolve();
            }).catch((err: any) => {
                console.log({ err });
                validateStatus["input"] = 'error';
                validateHelp["input"] = err;
                return Promise.reject();
            });
            const legal_suffix = [".pdf"];
            if (!legal_suffix.some((suffix) => value.trim().endsWith(suffix))) {
                validateStatus["input"] = 'error';
                validateHelp["input"] = "仅支持pdf格式的文件";
                return Promise.reject();
            }
        };
        const validateRange = async (_rule: Rule, value: string) => {
            validateStatus["page"] = 'validating';
            if (value.trim() === '') {
                validateStatus["page"] = 'success';
                validateHelp["page"] = '';
                return Promise.resolve();
            }
            await CheckRangeFormat(value).then((res: any) => {
                if (res) {
                    console.log({ res });
                    validateStatus["page"] = 'error';
                    validateHelp["page"] = res;
                    return Promise.reject();
                }
                validateStatus["page"] = 'success';
                validateHelp["page"] = res;
                return Promise.resolve();
            }).catch((err: any) => {
                console.log({ err });
                validateStatus["page"] = 'error';
                validateHelp["page"] = err;
                return Promise.reject();
            });
        };
        const validateHexColor = async (_rule: Rule, value: string) => {
            validateStatus["font_color"] = 'validating';
            if (value.trim() === '') {
                validateStatus["font_color"] = 'error';
                validateHelp["font_color"] = "请填写颜色";
                return Promise.reject();
            }
            const reg = /^#[0-9a-fA-f]{6}$/;
            if (!reg.test(value)) {
                validateStatus["font_color"] = 'error';
                validateHelp["font_color"] = "请填写正确的颜色";
                return Promise.reject();
            }
            validateStatus["font_color"] = 'success';
            validateHelp["font_color"] = '';
            return Promise.resolve();
        };
        const rules: Record<string, Rule[]> = {
            input: [{ required: true, validator: validateFileExists, trigger: 'change' }],
            page: [{ validator: validateRange, trigger: 'change' }],
            text: [{ required: true, message: "请填写水印文本", trigger: 'change' }],
            wm_path: [{ required: true, message: "请填写水印图片路径", trigger: 'change' }],
            font_color: [{ validator: validateHexColor, trigger: 'change' }],
        };
        // 重置表单
        const resetFields = () => {
            formRef.value?.resetFields();
        }
        // 提交表单
        const confirmLoading = ref<boolean>(false);
        async function submit() {
            confirmLoading.value = true;
            switch (formState.op) {
                case "add": {
                    switch (formState.type) {
                        case "text": {
                            await handleOps(WatermarkPDFByText, [
                                formState.input,
                                formState.output,
                                formState.text,
                                formState.font_family,
                                formState.font_size,
                                formState.font_color,
                                formState.rotate,
                                formState.font_opacity,
                                formState.num_lines,
                                formState.word_spacing,
                                formState.line_spacing,
                                formState.x_offset,
                                formState.y_offset,
                                formState.multiple_mode,
                                formState.layer,
                                formState.page
                            ]);
                            break;
                        }
                        case "image": {
                            await handleOps(WatermarkPDFByImage, [
                                formState.input,
                                formState.output,
                                formState.wm_path,
                                formState.rotate,
                                formState.font_opacity,
                                formState.scale,
                                formState.num_lines,
                                formState.line_spacing,
                                formState.word_spacing,
                                formState.x_offset,
                                formState.y_offset,
                                formState.multiple_mode,
                                formState.layer,
                                formState.page
                            ]);
                            break;
                        }
                        case "pdf": {
                            await handleOps(WatermarkPDFByPDF, [
                                formState.input,
                                formState.output,
                                formState.wm_path,
                                formState.layer,
                                formState.page]);
                            break;
                        }
                    }
                    break;
                }
                case "remove": {
                    switch (formState.remove_method) {
                        case "type": {
                            await handleOps(RemoveWatermarkByType, [formState.input, formState.output, formState.page]);
                            break;
                        }
                        case "index": {
                            switch (formState.step) {
                                case "1": {
                                    let wm_index = formState.wm_index.split(",").map((item) => parseInt(item.trim()));
                                    await handleOps(DetectWatermarkByIndex, [formState.input, formState.output, wm_index[0] - 1]);
                                    break;
                                }
                                case "2": {
                                    let wm_index = formState.wm_index.split(",").map((item) => parseInt(item.trim()) - 1);
                                    await handleOps(RemoveWatermarkByIndex, [formState.input, formState.output, wm_index, formState.page]);
                                    break;
                                }
                            }
                            break;
                        }
                        case "mask": {
                            switch (formState.mask_type) {
                                case "rect": {
                                    await handleOps(MaskPDFByRect, [formState.input, formState.output, [formState.x_offset, formState.y_offset, formState.x_offset + formState.width, formState.y_offset + formState.height], formState.unit, formState.mask_color, formState.mask_opacity, 0, formState.page]);
                                    break;
                                }
                                case "annot": {
                                    await handleOps(MaskPDFByAnnot, [formState.input, formState.output, formState.annot_page - 1, formState.mask_color, formState.mask_opacity, 0, formState.page]);
                                    break;
                                }
                            }
                            break;
                        }
                    }
                    break;
                }
            }
            confirmLoading.value = false;
        }
        const onFinish = async () => {
            await submit();
        }

        // @ts-ignore
        const onFinishFailed = async ({ values, errorFields, outOfDate }) => {
            if (errorFields.length > 0) {
                console.log({ errorFields });
                message.error("表单验证失败");
            }
            if (outOfDate) {
                // 忽略过期
                await submit();
            }
        }
        const selectFile = async (field: string) => {
            await SelectFile().then((res: string) => {
                console.log({ res });
                if (res) {
                    Object.assign(formState, { [field]: res });
                }
                formRef.value?.validateFields(field);
            }).catch((err: any) => {
                console.log({ err });
            });
        }
        const saveFile = async (field: string) => {
            await SaveFile().then((res: string) => {
                console.log({ res });
                if (res) {
                    Object.assign(formState, { [field]: res });
                }
                formRef.value?.validateFields(field);
            }).catch((err: any) => {
                console.log({ err });
            });
        }
        return {
            selectFile,
            saveFile,
            formState,
            color_picker_state,
            rules,
            formRef,
            validateStatus,
            validateHelp,
            confirmLoading,
            resetFields,
            onFinish,
            onFinishFailed,
            font_options,
        };
    }
})
</script>