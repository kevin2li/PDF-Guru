<template>
    <div>
        <a-form ref="formRef" style="border: 1px solid #dddddd; padding: 10px 0;border-radius: 10px;margin-right: 5vw;"
            :model="formState" :label-col="{ span: 3 }" :wrapper-col="{ offset: 1, span: 18 }" :rules="rules"
            @finish="onFinish" @finishFailed="onFinishFailed">
            <a-form-item name="op" label="提取类型">
                <a-radio-group button-style="solid" v-model:value="formState.op">
                    <a-radio-button value="page">页面</a-radio-button>
                    <a-radio-button value="text">文本</a-radio-button>
                    <a-radio-button value="image">图片</a-radio-button>
                    <a-radio-button value="table" disabled>表格</a-radio-button>
                </a-radio-group>
            </a-form-item>
            <a-form-item name="page" hasFeedback :validateStatus="validateStatus.page" :help="validateHelp.page"
                label="页码范围">
                <a-input v-model:value="formState.page" placeholder="应用的页码范围(留空表示全部), e.g. 1-10" allow-clear />
            </a-form-item>
            <a-form-item name="input" label="输入" hasFeedback :validateStatus="validateStatus.input"
                :help="validateHelp.input">
                <a-input v-model:value="formState.input" placeholder="输入文件路径" allow-clear />
            </a-form-item>
            <a-form-item name="output" label="输出">
                <a-input v-model:value="formState.output" placeholder="输出目录(留空则保存到输入文件同级目录)" allow-clear />
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
import { CheckFileExists, CheckRangeFormat, ReorderPDF, ExtractTextFromPDF, ExtractImageFromPDF } from '../../../wailsjs/go/main/App';
import type { FormInstance } from 'ant-design-vue';
import type { Rule } from 'ant-design-vue/es/form';
import type { ExtractState } from "../data";
import { handleOps } from "../data";
export default defineComponent({
    components: {
    },
    setup() {
        const formRef = ref<FormInstance>();
        const formState = reactive<ExtractState>({
            input: "",
            output: "",
            page: "",
            op: "page",
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
            formRef.value?.resetFields();
        }
        // 提交表单
        const confirmLoading = ref<boolean>(false);
        async function submit() {
            confirmLoading.value = true;
            switch (formState.op) {
                case "page": {
                    let output = formState.output.trim();
                    if (output === '') {
                        output = formState.input.replace(/\.pdf$/, "_提取.pdf");
                    }
                    await handleOps(ReorderPDF, [formState.input.trim(), output, formState.page]);
                    break;
                }
                case "text": {
                    await handleOps(ExtractTextFromPDF, [formState.input.trim(), formState.output.trim(), formState.page]);
                    break;
                }
                case "image": {
                    await handleOps(ExtractImageFromPDF, [formState.input.trim(), formState.output.trim(), formState.page]);
                    break;
                }
                case "table": {
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
        return { formState, rules, formRef, validateStatus, validateHelp, confirmLoading, resetFields, onFinish, onFinishFailed };
    }
})
</script>