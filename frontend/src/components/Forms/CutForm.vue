<template>
    <div>
        <a-form ref="formRef" style="border: 1px solid #dddddd; padding: 10px 0;border-radius: 10px;margin-right: 5vw;"
            :model="store" :label-col="{ span: 3 }" :wrapper-col="{ offset: 1, span: 18 }" :rules="rules" @finish="onFinish"
            @finishFailed="onFinishFailed">
            <a-form-item name="op" label="操作">
                <a-radio-group button-style="solid" v-model:value="store.op">
                    <a-radio-button value="split">分割</a-radio-button>
                    <a-radio-button value="combine">组合</a-radio-button>
                </a-radio-group>
            </a-form-item>
            <div v-if="store.op == 'split'">
                <a-form-item label="分割类型">
                    <a-radio-group v-model:value="store.split_type">
                        <a-radio value="even">均匀分割</a-radio>
                        <a-radio value="custom">自定义分割</a-radio>
                    </a-radio-group>
                </a-form-item>
                <a-form-item label="网格形状" v-if="store.split_type == 'even'">
                    <a-space size="large">
                        <a-input-number v-model:value="store.rows" :min="1">
                            <template #addonBefore>
                                行数
                            </template>
                        </a-input-number>
                        <a-input-number v-model:value="store.cols" :min="1">
                            <template #addonBefore>
                                列数
                            </template>
                        </a-input-number>
                    </a-space>
                </a-form-item>
                <a-form-item :label="index === 0 ? '水平分割线' : ' '" :colon="index === 0 ? true : false"
                    v-if="store.split_type == 'custom'" v-for="(item, index) in store.split_h_breakpoints" :key="index">
                    <a-input-number :min="0" :max="1" :step="0.01" v-model:value="store.split_h_breakpoints[index]" />
                    <MinusCircleOutlined @click="removeHBreakpoint(item)" style="margin-left: 1vw;" />
                </a-form-item>
                <a-form-item name="span" :label="store.split_h_breakpoints.length === 0 ? '水平分割线' : ' '"
                    :colon="store.split_h_breakpoints.length === 0 ? true : false" v-if="store.split_type == 'custom'">
                    <a-button type="dashed" block @click="addHBreakpoint">
                        <PlusOutlined />
                        添加水平分割线
                    </a-button>
                </a-form-item>
                <a-form-item :label="index === 0 ? '垂直分割线' : ' '" :colon="index === 0 ? true : false"
                    v-if="store.split_type == 'custom'" v-for="(item, index) in  store.split_v_breakpoints " :key="index">
                    <a-input-number :min="0" :max="1" :step="0.01" v-model:value="store.split_v_breakpoints[index]" />
                    <MinusCircleOutlined @click=" removeVBreakpoint(item)" style="margin-left: 1vw;" />
                </a-form-item>
                <a-form-item name="span" :label="store.split_v_breakpoints.length === 0 ? '垂直分割线' : ' '"
                    :colon="store.split_v_breakpoints.length === 0 ? true : false" v-if="store.split_type == 'custom'">
                    <a-button type="dashed" block @click="addVBreakpoint">
                        <PlusOutlined />
                        添加垂直分割线
                    </a-button>
                </a-form-item>
            </div>
            <div v-else>
                <a-form-item label="网格形状">
                    <a-space size="large">
                        <a-input-number v-model:value="store.rows" :min="1">
                            <template #addonBefore>
                                行数
                            </template>
                        </a-input-number>
                        <a-input-number v-model:value="store.cols" :min="1">
                            <template #addonBefore>
                                列数
                            </template>
                        </a-input-number>
                    </a-space>
                </a-form-item>
                <a-form-item name="paper_size" label="纸张大小">
                    <a-select v-model:value="store.paper_size" style="width: 200px">
                        <a-select-option value="same">与文档相同</a-select-option>
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
            </div>
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
import { defineComponent, reactive, watch, ref } from 'vue';
import { message, Modal } from 'ant-design-vue';
import {
    SelectFile,
    SaveFile,
    CheckFileExists,
    CheckRangeFormat,
    CutPDFByGrid,
    CutPDFByBreakpoints,
    CombinePDFByGrid
} from '../../../wailsjs/go/main/App';
import type { FormInstance } from 'ant-design-vue';
import type { Rule } from 'ant-design-vue/es/form';
import { MinusCircleOutlined, PlusOutlined, EllipsisOutlined } from '@ant-design/icons-vue';
import { handleOps } from "../data";
import { useCutState } from "../../store/cut";

export default defineComponent({
    components: {
        MinusCircleOutlined,
        PlusOutlined,
        EllipsisOutlined
    },
    setup() {
        const formRef = ref<FormInstance>();
        const store = useCutState();
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

        // 分割PDF
        const addHBreakpoint = () => {
            store.split_h_breakpoints.push(0);
        }
        const removeHBreakpoint = (item: number) => {
            const index = store.split_h_breakpoints.indexOf(item);
            if (index != -1) {
                store.split_h_breakpoints.splice(index, 1);
            }
        }
        const addVBreakpoint = () => {
            store.split_v_breakpoints.push(0);
        }
        const removeVBreakpoint = (item: number) => {
            const index = store.split_v_breakpoints.indexOf(item);
            if (index != -1) {
                store.split_v_breakpoints.splice(index, 1);
            }
        }
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
                case "split": {
                    if (store.split_type == "even") {
                        await handleOps(CutPDFByGrid, [store.input.trim(), store.output.trim(), store.rows, store.cols, store.page]);
                    } else {
                        await handleOps(CutPDFByBreakpoints, [store.input.trim(), store.output.trim(), store.split_h_breakpoints, store.split_v_breakpoints, store.page]);
                    }
                    break;
                }
                case "combine": {
                    await handleOps(CombinePDFByGrid, [store.input.trim(), store.output.trim(), store.rows, store.cols, store.page, store.paper_size, store.orientation]);
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

        return {
            selectFile,
            saveFile,
            store,
            rules,
            formRef,
            validateStatus,
            validateHelp,
            confirmLoading,
            addHBreakpoint,
            removeHBreakpoint,
            addVBreakpoint,
            removeVBreakpoint,
            resetFields,
            onFinish,
            onFinishFailed
        };
    }
})
</script>