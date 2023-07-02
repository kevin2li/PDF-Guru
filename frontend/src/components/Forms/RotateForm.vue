<template>
    <div>
        <a-form ref="formRef" style="border: 1px solid #dddddd; padding: 10px 0;border-radius: 10px;margin-right: 5vw;"
            :model="formState" :label-col="{ span: 3 }" :wrapper-col="{ offset: 1, span: 18 }" :rules="rules">
            <a-form-item name="rotate" label="旋转角度">
                <a-radio-group v-model:value="formState.degree">
                    <a-radio :value="90">顺时针90</a-radio>
                    <a-radio :value="180">顺时针180</a-radio>
                    <a-radio :value="270">逆时针90</a-radio>
                </a-radio-group>
            </a-form-item>
            <a-form-item name="page" hasFeedback :validateStatus="validateStatus.page" label="页码范围">
                <a-input v-model:value="formState.page" placeholder="应用的页码范围(留空表示全部), e.g. 1-10" allow-clear />
            </a-form-item>
            <a-form-item name="input" label="输入" hasFeedback :validateStatus="validateStatus.input">
                <a-input v-model:value="formState.input" placeholder="输入文件路径" allow-clear />
            </a-form-item>
            <a-form-item name="output" label="输出">
                <a-input v-model:value="formState.output" placeholder="输出目录" allow-clear />
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
import { CheckFileExists, CheckRangeFormat, RotatePDF } from '../../../wailsjs/go/main/App';
import type { FormInstance } from 'ant-design-vue';
import type { Rule } from 'ant-design-vue/es/form';
import type { RotateState } from "../data";
import { handleOps } from "../data";
export default defineComponent({
    components: {
    },
    setup() {
        const formRef = ref<FormInstance>();
        const formState = reactive<RotateState>({
            input: "",
            output: "",
            page: "",
            degree: 90,
        });

        const validateStatus = reactive({
            input: "",
            page: "",
        });

        const validateFileExists = async (_rule: Rule, value: string) => {
            validateStatus["input"] = 'validating';
            if (value === '') {
                validateStatus.input = 'error';
                return Promise.reject('请填写路径');
            }
            await CheckFileExists(value).then((res: any) => {
                console.log({ res });
                if (res) {
                    validateStatus["input"] = 'error';
                    return Promise.reject(res);
                }
                validateStatus["input"] = 'success';
                return Promise.resolve();
            }).catch((err: any) => {
                console.log({ err });
                validateStatus["input"] = 'error';
                return Promise.reject("文件不存在");
            });
        };
        const validateRange = async (_rule: Rule, value: string) => {
            validateStatus["page"] = 'validating';
            await CheckRangeFormat(value).then((res: any) => {
                console.log({ res });
                if (res) {
                    validateStatus["page"] = 'error';
                    return Promise.reject("页码格式错误");
                }
                validateStatus["page"] = 'success';
                return Promise.resolve();
            }).catch((err: any) => {
                console.log({ err });
                validateStatus["page"] = 'error';
                return Promise.reject("页码格式错误");
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
        const onSubmit = async () => {
            try {
                await formRef.value?.validate();
                confirmLoading.value = true;
                await handleOps(RotatePDF, [formState.input, formState.output, formState.degree, formState.page]);
                confirmLoading.value = false;
            } catch (err) {
                console.log({ err });
                message.error("表单验证失败");
            }
        }
        return { formState, rules, formRef, validateStatus, confirmLoading, resetFields, onSubmit };
    }
})
</script>