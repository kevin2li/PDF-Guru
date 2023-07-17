<template>
    <div>
        <a-form ref="formRef" style="border: 1px solid #dddddd; padding: 10px 0;border-radius: 10px;margin-right: 5vw;"
            :model="formState" :label-col="{ span: 3 }" :wrapper-col="{ offset: 1, span: 18 }" :rules="rules"
            @finish="onFinish" @finishFailed="onFinishFailed">
            <a-form-item name="op" label="类型">
                <a-radio-group button-style="solid" v-model:value="formState.op">
                    <a-radio-button value="span">均匀分块</a-radio-button>
                    <a-radio-button value="range">自定义范围</a-radio-button>
                    <a-radio-button value="bookmark">目录</a-radio-button>
                </a-radio-group>
            </a-form-item>
            <a-form-item name="span" label="块大小" v-if="formState.op == 'span'">
                <a-input-number v-model:value="formState.span" :min="1" />
            </a-form-item>
            <a-form-item name="page" label="页码范围" v-if="formState.op == 'range'" hasFeedback
                :validateStatus="validateStatus.page" :help="validateHelp.page">
                <a-input v-model:value="formState.page" placeholder="自定义页码范围,用英文逗号隔开,e.g. 1-10,11-15,16-19" />
            </a-form-item>
            <a-form-item name="bookmark_level" label="目录级别" v-if="formState.op == 'bookmark'">
                <a-select v-model:value="formState.bookmark_level" style="width: 200px">
                    <a-select-option value="1">一级标题</a-select-option>
                    <a-select-option value="2">二级标题</a-select-option>
                    <a-select-option value="3">三级标题</a-select-option>
                </a-select>
            </a-form-item>
            <a-form-item name="input" label="输入" :validateStatus="validateStatus.input" :help="validateHelp.input">
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
    SplitPDFByChunk,
    SplitPDFByPage,
    SplitPDFByBookmark
} from '../../../wailsjs/go/main/App';
import type { FormInstance } from 'ant-design-vue';
import type { Rule } from 'ant-design-vue/es/form';
import { EllipsisOutlined } from '@ant-design/icons-vue';
import type { SplitState } from "../data";
import { handleOps } from "../data";
export default defineComponent({
    components: {
        EllipsisOutlined
    },
    setup() {
        const formRef = ref<FormInstance>();
        const formState = reactive<SplitState>({
            input: "",
            output: "",
            page: "",
            op: "span",
            span: 5,
            bookmark_level: "1",
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
                if (res) {
                    console.log({ res });
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
            await CheckRangeFormat(value).then((res: any) => {
                console.log({ res });
                if (res) {
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
            switch (formState.op) {
                case "span": {
                    await handleOps(SplitPDFByChunk, [formState.input.trim(), formState.span, formState.output.trim()]);
                    break;
                }
                case "range": {
                    await handleOps(SplitPDFByPage, [formState.input.trim(), formState.page, formState.output.trim()]);
                    break;
                }
                case "bookmark": {
                    await handleOps(SplitPDFByBookmark, [formState.input.trim(), formState.bookmark_level, formState.output.trim()]);
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

        return { selectFile, formState, rules, formRef, validateStatus, validateHelp, confirmLoading, resetFields, onFinish, onFinishFailed };
    }
})
</script>