<template>
    <div>
        <a-form ref="formRef" style="border: 1px solid #dddddd; padding: 10px 0;border-radius: 10px;margin-right: 5vw;"
            :model="store" :label-col="{ span: 3 }" :wrapper-col="{ offset: 1, span: 18 }" :rules="rules"
            @finish="onFinish" @finishFailed="onFinishFailed">
            <a-form-item name="op" label="操作">
                <a-radio-group button-style="solid" v-model:value="store.op">
                    <a-radio-button value="ratio">按比例缩放</a-radio-button>
                    <a-radio-button value="common">缩放到指定大小</a-radio-button>
                    <a-radio-button value="custom">自定义长宽</a-radio-button>
                </a-radio-group>
            </a-form-item>
            <div v-if="store.op === 'ratio'">
                <a-form-item name="ratio" label="缩放比例">
                    <a-input-number v-model:value="store.ratio" :min="0"></a-input-number>
                </a-form-item>
            </div>
            <div v-if="store.op === 'common'">
                <a-form-item name="paper_size" label="纸张大小">
                    <a-select v-model:value="store.paper_size" style="width: 200px">
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
            </div>
            <div v-if="store.op === 'custom'">
                <a-form-item name="width" label="宽度">
                    <a-input-number v-model:value="store.width" :min="0"></a-input-number>
                </a-form-item>
                <a-form-item name="height" label="高度">
                    <a-input-number v-model:value="store.height" :min="0"></a-input-number>
                </a-form-item>
                <a-form-item label="单位">
                    <a-radio-group v-model:value="store.unit">
                        <a-radio value="pt">像素</a-radio>
                        <a-radio value="cm">厘米</a-radio>
                        <a-radio value="mm">毫米</a-radio>
                        <a-radio value="in">英寸</a-radio>
                    </a-radio-group>
                </a-form-item>
            </div>
            <a-form-item name="page" hasFeedback :validateStatus="validateStatus.page" :help="validateHelp.page"
                label="页码范围">
                <a-input v-model:value="store.page" placeholder="应用的页码范围(留空表示全部), e.g. 1-10" allow-clear />
            </a-form-item>
            <a-form-item name="input" label="输入" :validateStatus="validateStatus.input" :help="validateHelp.input">
                <div>
                    <a-row>
                        <a-col :span="22">
                            <a-input v-model:value="store.input" placeholder="输入文件路径, 支持使用*匹配多个文件, 如D:\test\*.pdf" allow-clear />
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
import { defineComponent, reactive, watch, ref } from 'vue';
import { message, Modal } from 'ant-design-vue';
import {
    SelectFile,
    SaveFile,
    CheckFileExists,
    CheckRangeFormat,
    ScalePDFByPaperSize,
    ScalePDFByScale,
    ScalePDFByDim
} from '../../../wailsjs/go/main/App';
import type { FormInstance } from 'ant-design-vue';
import { EllipsisOutlined } from '@ant-design/icons-vue';
import type { Rule } from 'ant-design-vue/es/form';
import type { ScaleState } from "../data";
import { handleOps } from "../data";
import {useScaleState} from "../../store/scale";

export default defineComponent({
    components: {
        EllipsisOutlined
    },
    setup() {
        const formRef = ref<FormInstance>();
        const store = useScaleState();

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
                validateStatus['input'] = 'error';
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
            if (store.op === "ratio") {
                await handleOps(ScalePDFByScale, [store.input, store.output, store.ratio, store.page]);
            } else if (store.op === "common") {
                await handleOps(ScalePDFByPaperSize, [store.input, store.output, store.paper_size, store.page]);
            } else if (store.op === "custom") {
                await handleOps(ScalePDFByDim, [store.input, store.output, store.width, store.height, store.unit, store.page]);
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
            onFinishFailed
        };
    }
})
</script>