<template>
    <div>
        <a-form ref="formRef" style="border: 1px solid #dddddd; padding: 10px 0;border-radius: 10px;margin-right: 5vw;"
            :model="formState" :label-col="{ span: 3 }" :wrapper-col="{ offset: 1, span: 18 }" :rules="rules"
            @finish="onFinish" @finishFailed="onFinishFailed">
            <a-form-item name="crop_op" label="类型">
                <a-radio-group button-style="solid" v-model:value="formState.op">
                    <a-radio-button value="margin">根据页边距</a-radio-button>
                    <a-radio-button value="bbox">根据锚框</a-radio-button>
                </a-radio-group>
            </a-form-item>
            <a-form-item label="单位">
                <a-radio-group v-model:value="formState.unit">
                    <a-radio value="pt">像素</a-radio>
                    <a-radio value="cm">厘米</a-radio>
                    <a-radio value="mm">毫米</a-radio>
                    <a-radio value="in">英寸</a-radio>
                </a-radio-group>
            </a-form-item>
            <a-form-item name="crop.type" label="页边距" v-if="formState.op === 'margin'">
                <a-space size="large">
                    <a-input-number v-model:value="formState.up" :min="0">
                        <template #addonBefore>
                            上
                        </template>
                    </a-input-number>
                    <a-input-number v-model:value="formState.down" :min="0">
                        <template #addonBefore>
                            下
                        </template>
                    </a-input-number>
                    <a-input-number v-model:value="formState.left" :min="0">
                        <template #addonBefore>
                            左
                        </template>
                    </a-input-number>
                    <a-input-number v-model:value="formState.right" :min="0">
                        <template #addonBefore>
                            右
                        </template>
                    </a-input-number>
                </a-space>
            </a-form-item>
            <a-form-item name="crop.type" label="锚框" v-if="formState.op === 'bbox'">
                <a-space size="large">
                    <a-input-number v-model:value="formState.up" :min="0">
                        <template #addonBefore>
                            左上x
                        </template>
                    </a-input-number>
                    <a-input-number v-model:value="formState.left" :min="0">
                        <template #addonBefore>
                            左上y
                        </template>
                    </a-input-number>
                    <a-input-number v-model:value="formState.down" :min="0">
                        <template #addonBefore>
                            右下x
                        </template>
                    </a-input-number>
                    <a-input-number v-model:value="formState.right" :min="0">
                        <template #addonBefore>
                            右下y
                        </template>
                    </a-input-number>
                </a-space>
            </a-form-item>
            <a-form-item label="保持页面尺寸">
                <a-switch v-model:checked="formState.keep_size" />
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
import { CheckFileExists, CheckRangeFormat, CropPDFByBBOX, CropPDFByMargin } from '../../../wailsjs/go/main/App';
import type { FormInstance } from 'ant-design-vue';
import type { Rule } from 'ant-design-vue/es/form';
import { MinusCircleOutlined, PlusOutlined } from '@ant-design/icons-vue';
import type { CropState } from "../data";
import { handleOps } from "../data";
export default defineComponent({
    components: {
        MinusCircleOutlined,
        PlusOutlined
    },
    setup() {
        const formRef = ref<FormInstance>();
        const formState = reactive<CropState>({
            input: "",
            output: "",
            page: "",
            op: "margin",
            unit: "pt",
            keep_size: true,
            up: 0,
            left: 0,
            down: 0,
            right: 0,
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
            if (formState.op === "margin") {
                let margin = [formState.up, formState.right, formState.down, formState.left];
                await handleOps(CropPDFByMargin, [formState.input, formState.output, margin, formState.unit, formState.keep_size, formState.page]);
            }
            else if (formState.op === "bbox") {
                let bbox = [formState.up, formState.left, formState.down, formState.right];
                await handleOps(CropPDFByBBOX, [formState.input, formState.output, bbox, formState.unit, formState.keep_size, formState.page]);
            }
            else {
                message.error("未知的操作类型");
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
        return {
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