<template>
    <div>
        <a-form ref="formRef" style="border: 1px solid #dddddd; padding: 10px 0;border-radius: 10px;margin-right: 5vw;"
            :model="formState" :label-col="{ span: 3 }" :wrapper-col="{ offset: 1, span: 18 }" :rules="rules">
            <a-form-item name="insert_op" label="操作">
                <a-radio-group button-style="solid" v-model:value="formState.op">
                    <a-radio-button value="insert">插入</a-radio-button>
                    <a-radio-button value="replace">替换</a-radio-button>
                </a-radio-group>
            </a-form-item>
            <a-form-item label="源PDF路径" name="src_path" hasFeedback :validateStatus="validateStatus.src_path"
                :help="validateHelp.src_path">
                <a-input v-model:value="formState.src_path"
                    :placeholder="formState.op === 'insert' ? '被插入的PDF路径' : '被替换的PDF路径'" allow-clear></a-input>
            </a-form-item>
            <a-form-item name="page" label="插入位置" v-if="formState.op == 'insert'">
                <a-tooltip>
                    <template #title>
                        插入到指定页码之前
                    </template>
                    <a-input-number v-model:value="formState.src_pos" placeholder="插入位置, e.g. 10" :min="1" />
                </a-tooltip>
            </a-form-item>
            <a-form-item name="src_range" hasFeedback :validateStatus="validateStatus.src_range"
                :help="validateHelp.src_range" label="页码范围" v-if="formState.op == 'replace'">
                <a-input v-model:value="formState.src_range" placeholder="被替换的页码范围(留空表示全部), e.g. 1-10" />
            </a-form-item>
            <a-form-item label="目标PDF路径" name="dst_path" hasFeedback :validateStatus="validateStatus.dst_path"
                :help="validateHelp.dst_path">
                <a-input v-model:value="formState.dst_path" placeholder="插入的PDF路径" allow-clear />
            </a-form-item>
            <a-form-item name="dst_range" hasFeedback :validateStatus="validateStatus.dst_range"
                :help="validateHelp.dst_range" label="页码范围">
                <a-input v-model:value="formState.dst_range" placeholder="目标PDF的页码范围(留空表示全部), e.g. 1-10" />
            </a-form-item>
            <a-form-item name="output" label="输出">
                <a-input v-model:value="formState.output" placeholder="输出目录(留空则保存到输入文件同级目录)" allow-clear />
            </a-form-item>
            <a-form-item :wrapperCol="{ offset: 4 }" style="margin-bottom: 10px;">
                <a-button type="primary" html-type="submit" @click="onSubmit" :loading="confirmLoading">确认</a-button>
                <a-button style="margin-left: 10px" @click="resetFields">重置</a-button>
            </a-form-item>
        </a-form>
    </div>
</template>
<script lang="ts">
import { defineComponent, reactive, watch, ref } from 'vue';
import { message, Modal } from 'ant-design-vue';
import { CheckFileExists, CheckRangeFormat, InsertPDF, ReplacePDF } from '../../../wailsjs/go/main/App';
import type { FormInstance } from 'ant-design-vue';
import type { Rule } from 'ant-design-vue/es/form';
import type { InsertState } from "../data";
import { handleOps } from "../data";
export default defineComponent({
    components: {
    },
    setup() {
        const formRef = ref<FormInstance>();
        const formState = reactive<InsertState>({
            input: "",
            output: "",
            page: "",
            op: "insert",
            src_pos: 1,
            src_path: "",
            dst_path: "",
            src_range: "",
            dst_range: ""
        });

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
            src_path: [{ required: true, validator: validateFileExists, trigger: 'change' }],
            dst_path: [{ required: true, validator: validateFileExists, trigger: 'change' }],
            src_range: [{ validator: validateRange, trigger: 'change' }],
            dst_range: [{ validator: validateRange, trigger: 'change' }],
        };
        // 重置表单
        const resetFields = () => {
            formRef.value?.resetFields();
        }
        // 提交表单
        const confirmLoading = ref<boolean>(false);
        const onSubmit = async () => {
            // await formRef.value?.validate().then(async () => {
            confirmLoading.value = true;
            switch (formState.op) {
                case "insert": {
                    await handleOps(InsertPDF, [formState.src_path, formState.dst_path, formState.src_pos, formState.dst_range, formState.output])
                    confirmLoading.value = false;
                    break;
                }
                case "replace": {
                    await handleOps(ReplacePDF, [formState.src_path, formState.dst_path, formState.src_range, formState.dst_range, formState.output])
                    confirmLoading.value = false;
                    break;
                }
            }
            confirmLoading.value = false;
            // }).catch((err: any) => {
            //     console.log({ err });
            //     message.error("表单验证失败");
            // })

        }
        return { formState, rules, formRef, validateStatus, validateHelp, confirmLoading, resetFields, onSubmit };
    }
})
</script>