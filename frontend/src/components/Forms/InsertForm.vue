<template>
    <div>
        <a-form ref="formRef" style="border: 1px solid #dddddd; padding: 10px 0;border-radius: 10px;margin-right: 5vw;"
            :model="store" :label-col="{ span: 3 }" :wrapper-col="{ offset: 1, span: 18 }" :rules="rules" @finish="onFinish"
            @finishFailed="onFinishFailed">
            <a-form-item name="op" label="操作">
                <a-radio-group button-style="solid" v-model:value="store.op">
                    <a-radio-button value="insert">插入</a-radio-button>
                    <a-radio-button value="replace">替换</a-radio-button>
                </a-radio-group>
            </a-form-item>
            <a-form-item label="类型" v-if="store.op === 'insert'">
                <a-radio-group v-model:value="store.insert_type">
                    <a-radio value="blank">插入空白页</a-radio>
                    <a-radio value="other">插入其他文件</a-radio>
                </a-radio-group>
            </a-form-item>
            <div v-if="store.op === 'insert' && store.insert_type === 'blank'">
                <a-form-item label="插入位置">
                    <a-select v-model:value="store.src_pos_type" style="width: 200px">
                        <a-select-option value="before_first">第一页之前</a-select-option>
                        <a-select-option value="after_first">第一页之后</a-select-option>
                        <a-select-option value="before_last">最后一页之前</a-select-option>
                        <a-select-option value="after_last">最后一页之后</a-select-option>
                        <a-select-option value="before_custom">指定页码之前</a-select-option>
                        <a-select-option value="after_custom">指定页码之后</a-select-option>
                    </a-select>
                </a-form-item>
                <a-form-item name="src_pos" label="页码" v-if="store.src_pos_type.endsWith('custom')">
                    <a-input-number v-model:value="store.src_pos" placeholder="插入位置, e.g. 10" :min="1" />
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
                <a-form-item label="插入页数">
                    <a-input-number v-model:value="store.count" :min="1" />
                </a-form-item>
                <a-form-item name="src_path" label="输入" :validateStatus="validateStatus.src_path"
                    :help="validateHelp.src_path">
                    <div>
                        <a-row>
                            <a-col :span="22">
                                <a-input v-model:value="store.src_path" placeholder="输入文件路径" allow-clear />
                            </a-col>
                            <a-col :span="1" style="margin-left: 1vw;">
                                <a-tooltip>
                                    <template #title>选择文件</template>
                                    <a-button @click="selectFile('src_path')"><ellipsis-outlined /></a-button>
                                </a-tooltip>
                            </a-col>
                        </a-row>
                    </div>
                </a-form-item>
            </div>
            <div v-if="store.op === 'insert' && store.insert_type === 'other'">
                <a-form-item label="插入位置">
                    <a-select v-model:value="store.src_pos_type" style="width: 200px">
                        <a-select-option value="before_first">第一页之前</a-select-option>
                        <a-select-option value="after_first">第一页之后</a-select-option>
                        <a-select-option value="before_last">最后一页之前</a-select-option>
                        <a-select-option value="after_last">最后一页之后</a-select-option>
                        <a-select-option value="before_custom">指定页码之前</a-select-option>
                        <a-select-option value="after_custom">指定页码之后</a-select-option>
                    </a-select>
                </a-form-item>
                <a-form-item name="src_pos" label="页码" v-if="store.src_pos_type.endsWith('custom')">
                    <a-input-number v-model:value="store.src_pos" placeholder="插入位置, e.g. 10" :min="1" />
                </a-form-item>
                <a-form-item label="源PDF路径" name="src_path" :validateStatus="validateStatus.src_path"
                    :help="validateHelp.src_path">
                    <div>
                        <a-row>
                            <a-col :span="22">
                                <a-input v-model:value="store.src_path" placeholder="被插入的PDF路径" allow-clear></a-input>
                            </a-col>
                            <a-col :span="1" style="margin-left: 1vw;">
                                <a-tooltip>
                                    <template #title>选择文件</template>
                                    <a-button @click="selectFile('src_path')"><ellipsis-outlined /></a-button>
                                </a-tooltip>
                            </a-col>
                        </a-row>
                    </div>
                </a-form-item>
                <a-form-item label="目标PDF路径" name="dst_path" hasFeedback :validateStatus="validateStatus.dst_path"
                    :help="validateHelp.dst_path">
                    <div>
                        <a-row>
                            <a-col :span="22">
                                <a-input v-model:value="store.dst_path" placeholder="插入的PDF路径" allow-clear />
                            </a-col>
                            <a-col :span="1" style="margin-left: 1vw;">
                                <a-tooltip>
                                    <template #title>选择文件</template>
                                    <a-button @click="selectFile('dst_path')"><ellipsis-outlined /></a-button>
                                </a-tooltip>
                            </a-col>
                        </a-row>
                    </div>
                </a-form-item>
                <a-form-item name="dst_range" hasFeedback :validateStatus="validateStatus.dst_range"
                    :help="validateHelp.dst_range" label="页码范围">
                    <a-input v-model:value="store.dst_range" placeholder="目标PDF的页码范围(留空表示全部), e.g. 1-10" />
                </a-form-item>
            </div>
            <div v-if="store.op == 'replace'">
                <a-form-item label="源PDF路径" name="src_path" :validateStatus="validateStatus.src_path"
                    :help="validateHelp.src_path">
                    <div>
                        <a-row>
                            <a-col :span="22">
                                <a-input v-model:value="store.src_path" placeholder="被插入的PDF路径" allow-clear></a-input>
                            </a-col>
                            <a-col :span="1" style="margin-left: 1vw;">
                                <a-tooltip>
                                    <template #title>选择文件</template>
                                    <a-button @click="selectFile('src_path')"><ellipsis-outlined /></a-button>
                                </a-tooltip>
                            </a-col>
                        </a-row>
                    </div>
                </a-form-item>
                <a-form-item name="src_range" hasFeedback :validateStatus="validateStatus.src_range"
                    :help="validateHelp.src_range" label="页码范围">
                    <a-input v-model:value="store.src_range" placeholder="被替换的页码范围(留空表示全部), e.g. 1-10" />
                </a-form-item>
                <a-form-item label="目标PDF路径" name="dst_path" :validateStatus="validateStatus.dst_path"
                    :help="validateHelp.dst_path">
                    <div>
                        <a-row>
                            <a-col :span="22">
                                <a-input v-model:value="store.dst_path" placeholder="插入的PDF路径" allow-clear />
                            </a-col>
                            <a-col :span="1" style="margin-left: 1vw;">
                                <a-tooltip>
                                    <template #title>选择文件</template>
                                    <a-button @click="selectFile('dst_path')"><ellipsis-outlined /></a-button>
                                </a-tooltip>
                            </a-col>
                        </a-row>
                    </div>
                </a-form-item>
                <a-form-item name="dst_range" hasFeedback :validateStatus="validateStatus.dst_range"
                    :help="validateHelp.dst_range" label="页码范围">
                    <a-input v-model:value="store.dst_range" placeholder="目标PDF的页码范围(留空表示全部), e.g. 1-10" />
                </a-form-item>
            </div>
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
    CheckFileExists,
    CheckRangeFormat,
    InsertPDF,
    InsertBlankPDF,
    ReplacePDF,
    SelectFile,
    SaveFile,
} from '../../../wailsjs/go/main/App';
import type { FormInstance } from 'ant-design-vue';
import type { Rule } from 'ant-design-vue/es/form';
import { EllipsisOutlined } from '@ant-design/icons-vue';
import { handleOps } from "../data";
import { useInsertState } from "../../store/insert";

export default defineComponent({
    components: {
        EllipsisOutlined
    },
    setup() {
        const formRef = ref<FormInstance>();
        const store = useInsertState();
        const validateStatus = reactive({
            src_path: "",
            dst_path: "",
            src_range: "",
            dst_range: "",
        });
        const validateHelp = reactive({
            src_path: "",
            dst_path: "",
            src_range: "",
            dst_range: "",
        });

        const validateFileExists = async (_rule: Rule, value: string) => {
            // @ts-ignore
            validateStatus[_rule.field] = 'validating';
            if (value === '') {
                // @ts-ignore
                validateStatus[_rule.field] = "error";
                // @ts-ignore
                validateHelp[_rule.field] = "请填写路径";
                return Promise.reject();
            }
            await CheckFileExists(value).then((res: any) => {
                console.log({ res });
                if (res) {
                    // @ts-ignore
                    validateStatus[_rule.field] = 'error';
                    // @ts-ignore
                    validateHelp[_rule.field] = res;
                    return Promise.reject();
                }
                // @ts-ignore
                validateStatus[_rule.field] = 'success';
                // @ts-ignore
                validateHelp[_rule.field] = '';
                return Promise.resolve();
            }).catch((err: any) => {
                console.log({ err });
                // @ts-ignore
                validateStatus[_rule.field] = 'error';
                // @ts-ignore
                validateHelp[_rule.field] = err;
                return Promise.reject();
            });
            const legal_suffix = [".pdf"];
            if (!legal_suffix.some((suffix) => value.trim().endsWith(suffix))) {
                // @ts-ignore
                validateStatus[_rule.field] = 'error';
                // @ts-ignore
                validateHelp[_rule.field] = "仅支持pdf格式的文件";
                return Promise.reject();
            }
        };
        const validateRange = async (_rule: Rule, value: string) => {
            // @ts-ignore
            validateStatus[_rule.field] = 'validating';
            await CheckRangeFormat(value).then((res: any) => {
                if (res) {
                    console.log({ res });
                    // @ts-ignore
                    validateStatus[_rule.field] = 'error';
                    // @ts-ignore
                    validateHelp[_rule.field] = res;
                    return Promise.reject();
                }
                // @ts-ignore
                validateStatus[_rule.field] = 'success';
                // @ts-ignore
                validateHelp[_rule.field] = res;
                return Promise.resolve();
            }).catch((err: any) => {
                console.log({ err });
                // @ts-ignore
                validateStatus[_rule.field] = 'error';
                // @ts-ignore
                validateHelp[_rule.field] = err;
                return Promise.reject();
            });
        };
        const rules: Record<string, Rule[]> = {
            src_path: [{ required: true, validator: validateFileExists, trigger: ['change', 'blur'] }],
            dst_path: [{ required: true, validator: validateFileExists, trigger: ['change', 'blur'] }],
            src_range: [{ required: true, validator: validateRange, trigger: ['change', 'blur'] }],
            dst_range: [{ validator: validateRange, trigger: ['change', 'blur'] }],
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
                case "insert": {
                    if (store.insert_type === "blank") {
                        await handleOps(InsertBlankPDF, [
                            store.src_path,
                            store.dst_path,
                            store.src_pos,
                            store.src_pos_type,
                            store.paper_size,
                            store.orientation,
                            store.count,
                            store.output
                        ]);
                    } else {
                        await handleOps(InsertPDF, [
                            store.src_path,
                            store.dst_path,
                            store.src_pos,
                            store.dst_range,
                            store.src_pos_type,
                            store.output
                        ]);
                    }
                    confirmLoading.value = false;
                    break;
                }
                case "replace": {
                    await handleOps(ReplacePDF, [store.src_path, store.dst_path, store.src_range, store.dst_range, store.output]);
                    confirmLoading.value = false;
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
            resetFields,
            onFinish,
            onFinishFailed
        };
    }
})
</script>