<template>
    <div>
        <a-form ref="formRef" style="border: 1px solid #dddddd; padding: 10px 0;border-radius: 10px;margin-right: 5vw;"
            :model="store" :label-col="{ span: 3 }" :wrapper-col="{ offset: 1, span: 18 }" :rules="rules" @finish="onFinish"
            @finishFailed="onFinishFailed">
            <a-form-item name="encrypt_op" label="操作" style="margin-bottom: 1.8vh;">
                <a-radio-group button-style="solid" v-model:value="store.op">
                    <a-radio-button value="add">添加页眉页脚</a-radio-button>
                    <a-radio-button value="remove">删除页眉页脚</a-radio-button>
                </a-radio-group>
            </a-form-item>
            <div v-if="store.op === 'add'">
                <div style="border: 1px solid #dddddd;border-radius: 10px;margin: 0 1vw;">
                    <a-form-item name="is_set_upw" label="设置页眉" :disabled="!store.is_set_header">
                        <a-checkbox v-model:checked="store.is_set_header"></a-checkbox>
                    </a-form-item>
                    <a-form-item name="header_left ? 'upw' : 'upw-none'" label="左侧">
                        <a-textarea v-model:value="store.header_left" placeholder="页眉左侧内容" allow-clear
                            :disabled="!store.is_set_header" />
                    </a-form-item>
                    <a-form-item name="header_center ? 'upw' : 'upw-none'" label="中间">
                        <a-textarea v-model:value="store.header_center" placeholder="页眉中间内容" allow-clear
                            :disabled="!store.is_set_header" />
                    </a-form-item>
                    <a-form-item name="header_right ? 'upw' : 'upw-none'" label="右侧">
                        <a-textarea v-model:value="store.header_right" placeholder="页眉右侧内容" allow-clear
                            :disabled="!store.is_set_header" />
                    </a-form-item>
                </div>
                <div style="border: 1px solid #dddddd;border-radius: 10px;margin: 1vw 1vw;">
                    <a-form-item name="is_set_upw" label="设置页脚" :disabled="!store.is_set_footer">
                        <a-checkbox v-model:checked="store.is_set_footer"></a-checkbox>
                    </a-form-item>
                    <a-form-item name="footer_left ? 'upw' : 'upw-none'" label="左侧">
                        <a-textarea v-model:value="store.footer_left" placeholder="页脚左侧内容" allow-clear
                            :disabled="!store.is_set_footer" />
                    </a-form-item>
                    <a-form-item name="footer_center ? 'upw' : 'upw-none'" label="中间">
                        <a-textarea v-model:value="store.footer_center" placeholder="页脚中间内容" allow-clear
                            :disabled="!store.is_set_footer" />
                    </a-form-item>
                    <a-form-item name="footer_right ? 'upw' : 'upw-none'" label="右侧">
                        <a-textarea v-model:value="store.footer_right" placeholder="页脚右侧内容" allow-clear
                            :disabled="!store.is_set_footer" />
                    </a-form-item>
                </div>
                <a-form-item name="watermark_font_size" label="字体属性" hasFeedback>
                    <div>
                        <a-row :gutter="10">
                            <a-col>
                                <a-select v-model:value="store.font_family" style="width: 200px" :options="font_options">
                                </a-select>
                            </a-col>
                            <a-col>
                                <a-tooltip>
                                    <template #title>字号</template>
                                    <a-input-number v-model:value="store.font_size" :min="1">
                                        <template #prefix>
                                            <font-size-outlined />
                                        </template>
                                    </a-input-number>
                                </a-tooltip>
                            </a-col>
                            <a-col>
                                <a-space>
                                    <a-tooltip>
                                        <template #title>字体颜色</template>
                                        <a-input v-model:value="store.font_color" placeholder="16进制字体颜色"
                                            :defaultValue="store.font_color" allow-clear>
                                            <template #prefix>
                                                <font-colors-outlined />
                                            </template>
                                        </a-input>
                                    </a-tooltip>
                                    <color-picker v-model:pureColor="pureColor" v-model:gradientColor="gradientColor"
                                        shape="square" use-type="pure" format="hex6" @pureColorChange="handleColorChange" />
                                </a-space>
                            </a-col>
                        </a-row>
                    </div>
                </a-form-item>
                <a-form-item label="不透明度">
                    <a-row>
                        <a-col :span="3">
                            <a-input-number v-model:value="store.opacity" :min="0" :max="1" :step="0.01">
                            </a-input-number>
                        </a-col>
                        <a-col :span="5">
                            <a-slider v-model:value="store.opacity" :min="0" :max="1" :step="0.01" />
                        </a-col>
                    </a-row>
                </a-form-item>
            </div>
            <div v-if="store.op === 'remove'">
                <a-form-item label="删除对象">
                    <a-checkbox-group v-model:value="store.remove_list">
                        <a-checkbox value="header">页眉</a-checkbox>
                        <a-checkbox value="footer">页脚</a-checkbox>
                    </a-checkbox-group>
                </a-form-item>
            </div>
            <a-form-item label="页边距单位">
                <a-radio-group v-model:value="store.unit">
                    <a-radio value="pt">像素</a-radio>
                    <a-radio value="cm">厘米</a-radio>
                    <a-radio value="mm">毫米</a-radio>
                    <a-radio value="in">英寸</a-radio>
                </a-radio-group>
            </a-form-item>
            <a-form-item name="crop.type" label="页边距">
                <a-space size="large">
                    <a-input-number v-model:value="store.up" :min="0">
                        <template #addonBefore>
                            上
                        </template>
                    </a-input-number>
                    <a-input-number v-model:value="store.down" :min="0">
                        <template #addonBefore>
                            下
                        </template>
                    </a-input-number>
                    <a-input-number v-model:value="store.left" :min="0">
                        <template #addonBefore>
                            左
                        </template>
                    </a-input-number>
                    <a-input-number v-model:value="store.right" :min="0">
                        <template #addonBefore>
                            右
                        </template>
                    </a-input-number>
                </a-space>
            </a-form-item>
            <a-form-item name="page" hasFeedback :validateStatus="validateStatus.page" :help="validateHelp.page"
                label="页码范围">
                <a-input v-model:value="store.page" placeholder="应用的页码范围(留空表示全部), e.g. 1-10" allow-clear />
            </a-form-item>
            <a-form-item name="input" label="输入" :validateStatus="validateStatus.input" :help="validateHelp.input">
                <div>
                    <a-row>
                        <a-col :span="22">
                            <a-input v-model:value="store.input" placeholder="输入文件路径, 支持使用*匹配多个文件, 如D:\test\*.pdf"
                                allow-clear />
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
                            <a-input v-model:value="store.output" placeholder="输出路径(留空则保存到输入文件同级目录)" allow-clear />
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
import { defineComponent, reactive, onMounted, ref, watch } from 'vue';
import { message, Modal } from 'ant-design-vue';
import {
    SelectFile,
    SaveFile,
    CheckOS,
    CheckFileExists,
    CheckRangeFormat,
    AddPDFHeaderAndFooter,
    RemovePDFHeaderAndFooter
} from '../../../wailsjs/go/main/App';
import type { FormInstance } from 'ant-design-vue';
import type { Rule } from 'ant-design-vue/es/form';
import { FontSizeOutlined, FontColorsOutlined, EllipsisOutlined } from '@ant-design/icons-vue';
import { handleOps, windows_fonts_options, mac_fonts_options } from "../data";
import type { SelectProps } from 'ant-design-vue';
import { useHeaderAndFooterState } from '../../store/header';
import { ColorPicker } from "vue3-colorpicker";
import "vue3-colorpicker/style.css";
// @ts-ignore
import { ColorInputWithoutInstance } from "tinycolor2";
export default defineComponent({
    components: {
        FontSizeOutlined,
        FontColorsOutlined,
        EllipsisOutlined,
        ColorPicker
    },
    setup() {
        const formRef = ref<FormInstance>();
        const store = useHeaderAndFooterState();
        const font_options = ref<SelectProps['options']>([]);

        const setFontOptions = async () => {
            await CheckOS().then((res: any) => {
                if (res === "windows") {
                    font_options.value = windows_fonts_options;
                } else if (res === "darwin") {
                    font_options.value = mac_fonts_options;
                    store.font_family = 'STHeiti Light.ttc';
                }
            }).catch((err: any) => {
                console.log({ err });
            })
        }
        onMounted(async () => {
            await setFontOptions();
        });
        const validateStatus = reactive({
            input: "",
            page: "",
        });
        const validateHelp = reactive({
            input: "",
            page: "",
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
        const rules: Record<string, Rule[]> = {
            input: [{ required: true, validator: validateFileExists, trigger: 'change' }],
            page: [{ validator: validateRange, trigger: 'change' }],
        };
        // 重置表单
        const resetFields = () => {
            formRef.value?.clearValidate();
            store.resetState();
        }
        // 提交表单
        const confirmLoading = ref<boolean>(false);
        async function submit() {
            confirmLoading.value = true;
            switch (store.op) {
                case "add": {
                    await handleOps(AddPDFHeaderAndFooter, [
                        store.input,
                        store.output,
                        store.header_left,
                        store.header_center,
                        store.header_right,
                        store.footer_left,
                        store.footer_center,
                        store.footer_right,
                        [store.up, store.down, store.left, store.right],
                        store.unit,
                        store.font_family,
                        store.font_size,
                        store.font_color,
                        store.opacity,
                        store.page,
                    ]);
                    break;
                }
                case "remove": {
                    await handleOps(RemovePDFHeaderAndFooter, [
                        store.input,
                        store.output,
                        [store.up, store.down, store.left, store.right],
                        store.remove_list,
                        store.unit,
                        store.page,
                    ])
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
                    Object.assign(store, { [field]: res });
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
                    Object.assign(store, { [field]: res });
                }
                formRef.value?.validateFields(field);
            }).catch((err: any) => {
                console.log({ err });
            });
        }

        const pureColor = ref<ColorInputWithoutInstance>(store.font_color);
        const gradientColor = ref("linear-gradient(0deg, rgba(0, 0, 0, 1) 0%, rgba(0, 0, 0, 1) 100%)");
        const handleColorChange = (color: ColorInputWithoutInstance) => {
            console.log({ color });
            store.font_color = color;
        }
        watch(() => store.font_color, (newVal, oldVal) => {
            console.log({ newVal, oldVal });
            pureColor.value = newVal;
        })
        return {
            selectFile,
            saveFile,
            store,
            rules,
            formRef,
            validateStatus,
            validateHelp,
            confirmLoading,
            resetFields,
            onFinish,
            onFinishFailed,
            font_options,
            pureColor,
            gradientColor,
            handleColorChange
        };
    }
})
</script>