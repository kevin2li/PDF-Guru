<template>
    <div>
        <a-form ref="formRef" style="border: 1px solid #dddddd; padding: 10px 0;border-radius: 10px;margin-right: 5vw;"
            :model="store" :label-col="{ span: 3 }" :wrapper-col="{ offset: 1, span: 18 }" :rules="rules" @finish="onFinish"
            @finishFailed="onFinishFailed">
            <a-form-item name="type" label="转换类型">
                <a-select v-model:value="store.type" style="width: 300px">
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
                        <a-select-option value="mobi2pdf-python">mobi转pdf</a-select-option>
                        <a-select-option value="md2pdf" disabled>
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
                        <a-select-option value="tex2pdf" disabled>
                            latex转pdf
                            <a-tag color="blue">pandoc</a-tag>
                        </a-select-option>
                        <a-select-option value="epub2pdf" disabled>
                            epub转pdf
                            <a-tag color="blue">pandoc</a-tag>
                        </a-select-option>
                    </a-select-opt-group>
                </a-select>
            </a-form-item>
            <div v-if="store.type === 'pdf2png' || store.type === 'pdf2svg'">
                <a-form-item name="dpi" label="分辨率" v-if="store.type === 'pdf2png'">
                    <a-input-number v-model:value="store.dpi" style="width: 200px" min="1" max="1000" />
                </a-form-item>
                <a-form-item name="page" hasFeedback :validateStatus="validateStatus.page" :help="validateHelp.page"
                    label="页码范围" v-if="store.type.startsWith('pdf')">
                    <a-input v-model:value="store.page" placeholder="应用的页码范围(留空表示全部), e.g. 1-3,9-10" allow-clear />
                </a-form-item>
                <a-form-item name="input" label="输入" :validateStatus="validateStatus.input" :help="validateHelp.input">
                    <div v-if="store.sort_method !== 'custom'">
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
                                <a-input v-model:value="store.output" placeholder="输出目录(留空则保存到输入文件同级目录)" allow-clear />
                            </a-col>
                            <a-col :span="1" style="margin-left: 1vw;">
                                <a-tooltip>
                                    <template #title>选择目录</template>
                                    <a-button @click="saveDir('output')"><ellipsis-outlined /></a-button>
                                </a-tooltip>
                            </a-col>
                        </a-row>
                    </div>
                </a-form-item>
            </div>
            <div v-else-if="store.type === 'png2pdf' || store.type === 'svg2pdf'">
                <a-form-item label="纸张大小">
                    <a-select v-model:value="store.paper_size" style="width: 200px">
                        <a-select-option value="same">与图片相同</a-select-option>
                        <a-select-option value="a0">A0</a-select-option>
                        <a-select-option value="a1">A1</a-select-option>
                        <a-select-option value="a2">A2</a-select-option>
                        <a-select-option value="a3">A3</a-select-option>
                        <a-select-option value="a4">A4</a-select-option>
                        <a-select-option value="a5">A5</a-select-option>
                        <a-select-option value="a6">A6</a-select-option>
                        <a-select-option value="a7">A7</a-select-option>
                        <a-select-option value="a8">A8</a-select-option>
                        <a-select-option value="a9">A9</a-select-option>
                        <a-select-option value="a10">A10</a-select-option>
                        <a-select-option value="b0">B0</a-select-option>
                        <a-select-option value="b1">B1</a-select-option>
                        <a-select-option value="b2">B2</a-select-option>
                        <a-select-option value="b3">B3</a-select-option>
                        <a-select-option value="b4">B4</a-select-option>
                        <a-select-option value="b5">B5</a-select-option>
                        <a-select-option value="b6">B6</a-select-option>
                        <a-select-option value="b7">B7</a-select-option>
                        <a-select-option value="b8">B8</a-select-option>
                        <a-select-option value="b9">B9</a-select-option>
                        <a-select-option value="b10">B10</a-select-option>
                        <a-select-option value="c0">C0</a-select-option>
                        <a-select-option value="c1">C1</a-select-option>
                        <a-select-option value="c2">C2</a-select-option>
                        <a-select-option value="c3">C3</a-select-option>
                        <a-select-option value="c4">C4</a-select-option>
                        <a-select-option value="c5">C5</a-select-option>
                        <a-select-option value="c6">C6</a-select-option>
                        <a-select-option value="c7">C7</a-select-option>
                        <a-select-option value="c8">C8</a-select-option>
                        <a-select-option value="c9">C9</a-select-option>
                        <a-select-option value="c10">C10</a-select-option>
                        <a-select-option value="card-4x6">card-4x6</a-select-option>
                        <a-select-option value="card-5x7">card-5x7</a-select-option>
                        <a-select-option value="commercial">commercial</a-select-option>
                        <a-select-option value="executive">executive</a-select-option>
                        <a-select-option value="invoice">invoice</a-select-option>
                        <a-select-option value="ledger">ledger</a-select-option>
                        <a-select-option value="legal">legal</a-select-option>
                        <a-select-option value="legal-13">legal-13</a-select-option>
                        <a-select-option value="letter">letter</a-select-option>
                        <a-select-option value="monarch">monarch</a-select-option>
                        <a-select-option value="tabloid-extra">tabloid-extra</a-select-option>
                    </a-select>
                </a-form-item>
                <a-form-item label="纸张方向">
                    <a-radio-group v-model:value="store.orientation">
                        <a-radio value="portrait">纵向</a-radio>
                        <a-radio value="landscape">横向</a-radio>
                    </a-radio-group>
                </a-form-item>
                <a-form-item name="is_merge" label="是否合并">
                    <a-checkbox v-model:checked="store.is_merge"></a-checkbox>
                </a-form-item>
                <div v-if="store.is_merge">
                    <a-form-item name="sort_method" label="排序方式">
                        <a-radio-group v-model:value="store.sort_method">
                            <a-radio value="name">文件名(字母)</a-radio>
                            <a-radio value="name_digit">文件名(编号)</a-radio>
                            <a-radio value="ctime">创建时间</a-radio>
                            <a-radio value="mtime">修改时间</a-radio>
                            <a-radio value="custom">自定义</a-radio>
                        </a-radio-group>
                    </a-form-item>
                    <div v-if="store.sort_method !== 'custom'">
                        <a-form-item name="sort_direction" label="排序方向">
                            <a-radio-group v-model:value="store.sort_direction">
                                <a-radio value="asc">升序</a-radio>
                                <a-radio value="desc">降序</a-radio>
                            </a-radio-group>
                        </a-form-item>
                        <a-form-item name="input" label="输入" :validateStatus="validateStatus.input"
                            :help="validateHelp.input">
                            <div>
                                <a-row>
                                    <a-col :span="22">
                                        <a-input v-model:value="store.input"
                                            placeholder="输入文件路径, 支持使用*匹配多个文件, 如D:\test\*.pdf" allow-clear />
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
                    </div>
                    <div v-else>
                        <a-form-item :label="index === 0 ? '输入路径列表' : ' '" :colon="index === 0 ? true : false"
                            v-for="(item, index) in store.input_list" :key="index">
                            <a-input v-model:value="store.input_list[index]" style="width: 90%;" allow-clear
                                placeholder="输入文件路径" />
                            <MinusCircleOutlined @click="removePath(item)" style="margin-left: 1vw;" />
                        </a-form-item>
                        <a-form-item name="span" :label="store.input_list.length === 0 ? '输入路径列表' : ' '"
                            :colon="store.input_list.length === 0 ? true : false">
                            <a-button type="dashed" block @click="addPath">
                                <PlusOutlined />
                                添加路径
                            </a-button>
                        </a-form-item>
                    </div>
                    <a-form-item name="output" label="输出路径">
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
                </div>
                <div v-else>
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
                    <a-form-item name="output" label="输出目录">
                        <div>
                            <a-row>
                                <a-col :span="22">
                                    <a-input v-model:value="store.output" placeholder="输出目录(留空则保存到输入文件同级目录)" allow-clear />
                                </a-col>
                                <a-col :span="1" style="margin-left: 1vw;">
                                    <a-tooltip>
                                        <template #title>选择文件</template>
                                        <a-button @click="saveDir('output')"><ellipsis-outlined /></a-button>
                                    </a-tooltip>
                                </a-col>
                            </a-row>
                        </div>
                    </a-form-item>
                </div>
            </div>
            <div v-else>
                <a-form-item name="page" hasFeedback :validateStatus="validateStatus.page" :help="validateHelp.page"
                    label="页码范围" v-if="store.type.startsWith('pdf')">
                    <a-input v-model:value="store.page" placeholder="应用的页码范围(留空表示全部), e.g. 1-3,9-10" allow-clear />
                </a-form-item>
                <a-form-item name="input" label="输入" :validateStatus="validateStatus.input" :help="validateHelp.input">
                    <div>
                        <a-row>
                            <a-col :span="22">
                                <a-input v-model:value="store.input" placeholder="输入文件路径, 支持使用*匹配多个文件" allow-clear />
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
                <a-form-item name="output" label="输出目录">
                    <div>
                        <a-row>
                            <a-col :span="22">
                                <a-input v-model:value="store.output" placeholder="输出目录(留空则保存到输入文件同级目录)" allow-clear />
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
            </div>
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
    SaveFile,
    SelectMultipleFiles,
    SelectDir,
    CheckFileExists,
    CheckRangeFormat,
    PDFConversion,
    ConvertPDF2Docx,
    PandocConvert,
} from '../../../wailsjs/go/main/App';
import type { FormInstance } from 'ant-design-vue';
import {
    EllipsisOutlined,
    MinusCircleOutlined,
    PlusOutlined,
} from '@ant-design/icons-vue';
import type { Rule } from 'ant-design-vue/es/form';
import { handleOps } from "../data";
import { useConvertState } from '../../store/convert';

export default defineComponent({
    components: {
        EllipsisOutlined,
        MinusCircleOutlined,
        PlusOutlined,
    },
    setup() {
        const formRef = ref<FormInstance>();
        const store = useConvertState();
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
            formRef.value?.clearValidate();
            store.resetState();
        }
        // 提交表单
        const confirmLoading = ref<boolean>(false);
        async function submit() {
            confirmLoading.value = true;
            switch (store.type) {
                case "pdf2png": {
                    await handleOps(PDFConversion, [
                        [store.input],
                        store.output,
                        store.dpi,
                        false,
                        store.sort_method,
                        store.sort_direction,
                        "pdf",
                        "png",
                        store.paper_size,
                        store.orientation,
                        store.page,
                    ])
                    break;
                }
                case "pdf2svg": {
                    await handleOps(PDFConversion, [
                        [store.input],
                        store.output,
                        store.dpi,
                        false,
                        store.sort_method,
                        store.sort_direction,
                        "pdf",
                        "svg",
                        store.paper_size,
                        store.orientation,
                        store.page,
                    ])
                    break;
                }
                case "pdf2docx": {
                    await handleOps(ConvertPDF2Docx, [
                        store.input,
                        store.output,
                    ])
                    break;
                }
                case "pdf2image-pdf": {
                    await handleOps(PDFConversion, [
                        [store.input],
                        store.output,
                        store.dpi,
                        false,
                        store.sort_method,
                        store.sort_direction,
                        "pdf",
                        "image-pdf",
                        store.paper_size,
                        store.orientation,
                        store.page,
                    ])
                    break;
                }
                case "png2pdf": {
                    let input = [store.input];
                    if (store.is_merge && store.sort_method === "custom") {
                        input = store.input_list;
                    }
                    await handleOps(PDFConversion, [
                        input,
                        store.output,
                        store.dpi,
                        store.is_merge,
                        store.sort_method,
                        store.sort_direction,
                        "png",
                        "pdf",
                        store.paper_size,
                        store.orientation,
                        store.page,
                    ])
                    break;
                }
                case "svg2pdf": {
                    let input = [store.input];
                    if (store.is_merge && store.sort_method === "custom") {
                        input = store.input_list;
                    }
                    await handleOps(PDFConversion, [
                        input,
                        store.output,
                        store.dpi,
                        store.is_merge,
                        store.sort_method,
                        store.sort_direction,
                        "svg",
                        "pdf",
                        store.paper_size,
                        store.orientation,
                        store.page,
                    ])
                    break;
                }
                case "epub2pdf-python": {
                    await handleOps(PDFConversion, [
                        [store.input],
                        store.output,
                        store.dpi,
                        false,
                        store.sort_method,
                        store.sort_direction,
                        "epub",
                        "pdf",
                        store.paper_size,
                        store.orientation,
                        store.page,
                    ])
                    break;
                }
                case "mobi2pdf-python": {
                    await handleOps(PDFConversion, [
                        [store.input],
                        store.output,
                        store.dpi,
                        false,
                        store.sort_method,
                        store.sort_direction,
                        "mobi",
                        "pdf",
                        store.paper_size,
                        store.orientation,
                        store.page,
                    ])
                    break;
                }

                // pandoc
                case "md2docx": {
                    await handleOps(PandocConvert, [
                        store.input,
                        store.output,
                        ".docx"
                    ])
                    break;
                }
                case "docx2md": {
                    await handleOps(PandocConvert, [
                        store.input,
                        store.output,
                        ".md"
                    ])
                    break;
                }
                case "md2tex": {
                    await handleOps(PandocConvert, [
                        store.input,
                        store.output,
                        ".tex"
                    ])
                    break;
                }
                case "tex2md": {
                    await handleOps(PandocConvert, [
                        store.input,
                        store.output,
                        ".md"
                    ])
                    break;
                }

                case "md2html": {
                    await handleOps(PandocConvert, [
                        store.input,
                        store.output,
                        ".html"
                    ])
                    break;
                }
                case "md2js": {
                    await handleOps(PandocConvert, [
                        store.input,
                        store.output,
                        ".html"
                    ])
                    break;
                }
                case "html2md": {
                    await handleOps(PandocConvert, [
                        store.input,
                        store.output,
                        ".md"
                    ])
                    break;
                }
                case "tex2pdf": {
                    await handleOps(PandocConvert, [
                        store.input,
                        store.output,
                        ".pdf"
                    ])
                    break;
                }
                case "docx2html": {
                    await handleOps(PandocConvert, [
                        store.input,
                        store.output,
                        ".html"
                    ])
                    break;
                }
                case "md2pdf": {
                    await handleOps(PandocConvert, [
                        store.input,
                        store.output,
                        ".pdf"
                    ])
                    break;
                }
                case "epub2pdf": {
                    await handleOps(PandocConvert, [
                        store.input,
                        store.output,
                        ".pdf"
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
        const saveDir = async (field: string) => {
            await SelectDir().then((res: string) => {
                console.log({ res });
                if (res) {
                    Object.assign(store, { [field]: res });
                }
                formRef.value?.validateFields(field);
            }).catch((err: any) => {
                console.log({ err });
            });
        }

        const addPath = async () => {
            await SelectMultipleFiles().then((res: any) => {
                console.log({ res });
                if (res) {
                    store.input_list.push(...res);
                }
                formRef.value?.validateFields("input_list");
            }).catch((err: any) => {
                console.log({ err });
            });
        }
        const removePath = (item: string) => {
            const index = store.input_list.indexOf(item);
            if (index != -1) {
                store.input_list.splice(index, 1);
            }
        }
        return {
            selectFile,
            saveFile,
            saveDir,
            store,
            rules,
            formRef,
            validateStatus,
            validateHelp,
            confirmLoading,
            resetFields,
            onFinish,
            onFinishFailed,
            addPath,
            removePath,
        };
    }
})
</script>
