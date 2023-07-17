<template>
    <div>
        <a-form ref="formRef" style="border: 1px solid #dddddd; padding: 10px 0;border-radius: 10px;margin-right: 5vw;"
            :model="formState" :label-col="{ span: 3 }" :wrapper-col="{ offset: 1, span: 18 }" :rules="rules"
            @finish="onFinish" @finishFailed="onFinishFailed">
            <a-form-item name="convert_type" label="转换类型">
                <a-select v-model:value="formState.type" style="width: 300px" listHeight="150px">
                    <a-select-opt-group label="PDF转其他">
                        <a-select-option value="pdf2png">pdf转png</a-select-option>
                        <a-select-option value="pdf2svg">pdf转svg</a-select-option>
                        <a-select-option value="pdf2image-pdf">pdf转图片型pdf</a-select-option>
                        <!-- <a-select-option value="pdf2html">pdf转html</a-select-option> -->
                        <a-select-option value="pdf2docx">
                            pdf转docx
                            <a-tag color="blue">python</a-tag>
                        </a-select-option>
                    </a-select-opt-group>
                    <a-select-opt-group label="其他转PDF">
                        <a-select-option value="png2pdf">png转pdf</a-select-option>
                        <a-select-option value="svg2pdf">svg转pdf</a-select-option>
                        <a-select-option value="epub2pdf-python">epub转pdf</a-select-option>
                        <a-select-option value="mobi2pdf">mobi转pdf</a-select-option>
                        <a-select-option value="md2pdf">
                            markdown转pdf
                            <a-tag color="blue">pandoc</a-tag>
                        </a-select-option>
                        <!-- <a-select-option value="docx2pdf">word转pdf</a-select-option> -->
                    </a-select-opt-group>
                    <a-select-opt-group label="其他转换">
                        <a-select-option value="md2docx">
                            markdown转docx
                            <a-tag color="blue">pandoc</a-tag>
                        </a-select-option>
                        <a-select-option value="docx2md">
                            docx转markown
                            <a-tag color="blue">pandoc</a-tag>
                        </a-select-option>
                        <a-select-option value="md2tex">
                            markdown转latex
                            <a-tag color="blue">pandoc</a-tag>
                        </a-select-option>
                        <a-select-option value="tex2md">
                            latex转markdown
                            <a-tag color="blue">pandoc</a-tag>
                        </a-select-option>
                        <a-select-option value="md2html">
                            markdown转html
                            <a-tag color="blue">pandoc</a-tag>
                        </a-select-option>
                        <a-select-option value="md2js">
                            markdown转reveal.js
                            <a-tag color="blue">pandoc</a-tag>
                        </a-select-option>
                        <a-select-option value="html2md">
                            html转markdown
                            <a-tag color="blue">pandoc</a-tag>
                        </a-select-option>
                        <a-select-option value="tex2pdf">
                            latex转pdf
                            <a-tag color="blue">pandoc</a-tag>
                        </a-select-option>
                        <a-select-option value="epub2pdf">
                            epub转pdf
                            <a-tag color="blue">pandoc</a-tag>
                        </a-select-option>
                    </a-select-opt-group>
                </a-select>
            </a-form-item>
            <div v-if="formState.type === 'pdf2png'">
                <a-form-item name="dpi" label="分辨率">
                    <a-input-number v-model:value="formState.dpi" style="width: 200px" min="1" max="1000" />
                </a-form-item>
            </div>
            <a-form-item name="page" hasFeedback :validateStatus="validateStatus.page" :help="validateHelp.page"
                label="页码范围" v-if="formState.type.startsWith('pdf')">
                <a-input v-model:value="formState.page" placeholder="应用的页码范围(留空表示全部), e.g. 1-3,9-10" allow-clear />
            </a-form-item>
            <a-form-item name="input" label="输入"  :validateStatus="validateStatus.input"
                :help="validateHelp.input">
                <div>
                    <a-row>
                        <a-col :span="22">
                            <a-input v-model:value="formState.input" placeholder="输入文件路径" allow-clear />
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
                                <a-button @click="selectFile('output')"><ellipsis-outlined /></a-button>
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
import { defineComponent, reactive, watch, ref } from 'vue';
import { message, Modal } from 'ant-design-vue';
import {
    SelectFile,
    CheckFileExists,
    CheckRangeFormat,
    ConvertPDF2Docx,
    ConvertMd2Docx,
    ConvertMd2PDF,
    ConvertMd2Html,
    ConvertMd2Tex,
    PDFConversion,
} from '../../../wailsjs/go/main/App';
import type { FormInstance } from 'ant-design-vue';
import { EllipsisOutlined } from '@ant-design/icons-vue';
import type { Rule } from 'ant-design-vue/es/form';
import type { ConvertState } from "../data";
import { handleOps } from "../data";
export default defineComponent({
    components: {
        EllipsisOutlined
    },
    setup() {
        const formRef = ref<FormInstance>();
        const formState = reactive<ConvertState>({
            input: "",
            output: "",
            page: "",
            type: "pdf2png",
            dpi: 300,
            is_merge: false,
        });

        const validateStatus = reactive({
            input: "",
            page: "",
        });
        const validateHelp = reactive({
            input: "",
            page: "",
        })
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
            formRef.value?.resetFields();
        }
        // 提交表单
        const confirmLoading = ref<boolean>(false);
        async function submit() {
            confirmLoading.value = true;
            switch (formState.type) {
                case "pdf2png": {
                    await handleOps(PDFConversion, [
                        formState.input,
                        formState.output,
                        formState.dpi,
                        false,
                        "pdf",
                        "png",
                        formState.page,
                    ])
                    break;
                }
                case "png2pdf": {
                    await handleOps(PDFConversion, [
                        formState.input,
                        formState.output,
                        formState.dpi,
                        false,
                        "png",
                        "pdf",
                        formState.page,
                    ])
                    break;
                }
                case "pdf2svg": {
                    await handleOps(PDFConversion, [
                        formState.input,
                        formState.output,
                        formState.dpi,
                        false,
                        "pdf",
                        "svg",
                        formState.page,
                    ])
                    break;
                }
                case "svg2pdf": {
                    await handleOps(PDFConversion, [
                        formState.input,
                        formState.output,
                        formState.dpi,
                        false,
                        "svg",
                        "pdf",
                        formState.page,
                    ])
                    break;
                }
                case "epub2pdf-python": {
                    await handleOps(PDFConversion, [
                        formState.input,
                        formState.output,
                        formState.dpi,
                        false,
                        "epub",
                        "pdf",
                        formState.page,
                    ])
                    break;
                }
                case "mobi2pdf": {
                    await handleOps(PDFConversion, [
                        formState.input,
                        formState.output,
                        formState.dpi,
                        false,
                        "mobi",
                        "pdf",
                        formState.page,
                    ])
                    break;
                }
                case "pdf2docx": {
                    await handleOps(ConvertPDF2Docx, [
                        formState.input,
                        formState.output,
                    ])
                    break;
                }
                case "pdf2image-pdf": {
                    await handleOps(PDFConversion, [
                        formState.input,
                        formState.output,
                        formState.dpi,
                        false,
                        "pdf",
                        "image-pdf",
                        formState.page,
                    ])
                    break;
                }
                // pandoc
                case "md2docx": {
                    await handleOps(ConvertMd2Docx, [
                        formState.input,
                        formState.output,
                    ])
                    break;
                }
                case "md2pdf": {
                    await handleOps(ConvertMd2PDF, [
                        formState.input,
                        formState.output,
                    ])
                    break;
                }
                case "md2html": {
                    await handleOps(ConvertMd2Html, [
                        formState.input,
                        formState.output,
                    ])
                    break;
                }
                case "md2tex": {
                    await handleOps(ConvertMd2Tex, [
                        formState.input,
                        formState.output,
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
                    Object.assign(formState, { [field]: res });
                }
                formRef.value?.validateFields(field);
            }).catch((err: any) => {
                console.log({ err });
            });
        }
        return {
            selectFile,
            formState,
            rules,
            formRef,
            validateStatus,
            validateHelp,
            confirmLoading,
            resetFields,
            onFinish,
            onFinishFailed
        };
    }
})
</script>