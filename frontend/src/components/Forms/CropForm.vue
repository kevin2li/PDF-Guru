<template>
    <div>
        <a-form ref="formRef" style="border: 1px solid #dddddd; padding: 10px 0;border-radius: 10px;margin-right: 5vw;"
            :model="store" :label-col="{ span: 3 }" :wrapper-col="{ offset: 1, span: 18 }" :rules="rules" @finish="onFinish"
            @finishFailed="onFinishFailed">
            <a-form-item name="crop_op" label="类型">
                <a-radio-group button-style="solid" v-model:value="store.op">
                    <a-radio-button value="margin">根据页边距</a-radio-button>
                    <a-radio-button value="bbox">根据锚框</a-radio-button>
                    <a-radio-button value="annot">根据矩形注释</a-radio-button>
                </a-radio-group>
            </a-form-item>
            <div v-if="store.op !== 'annot'">
                <a-form-item label="单位">
                    <a-radio-group v-model:value="store.unit">
                        <a-radio value="pt">像素</a-radio>
                        <a-radio value="cm">厘米</a-radio>
                        <a-radio value="mm">毫米</a-radio>
                        <a-radio value="in">英寸</a-radio>
                    </a-radio-group>
                </a-form-item>
            </div>
            <div v-if="store.op === 'margin'">
                <a-form-item name="" label="页边距">
                    <a-space size="large">
                        <a-input-number v-model:value="store.up" :min="0">
                            <template #addonBefore>
                                上
                            </template>
                        </a-input-number>
                        <a-input-number v-model:value="store.down" :min="0">
                            <template #addonBefore>
                                下
                            </template>
                        </a-input-number>
                        <a-input-number v-model:value="store.left" :min="0">
                            <template #addonBefore>
                                左
                            </template>
                        </a-input-number>
                        <a-input-number v-model:value="store.right" :min="0">
                            <template #addonBefore>
                                右
                            </template>
                        </a-input-number>
                    </a-space>
                </a-form-item>
            </div>
            <div v-if="store.op === 'bbox'">
                <a-form-item name="crop.type" label="锚框">
                    <a-space size="large">
                        <a-input-number v-model:value="store.up" :min="0">
                            <template #addonBefore>
                                左上x
                            </template>
                        </a-input-number>
                        <a-input-number v-model:value="store.left" :min="0">
                            <template #addonBefore>
                                左上y
                            </template>
                        </a-input-number>
                        <a-input-number v-model:value="store.down" :min="0">
                            <template #addonBefore>
                                右下x
                            </template>
                        </a-input-number>
                        <a-input-number v-model:value="store.right" :min="0">
                            <template #addonBefore>
                                右下y
                            </template>
                        </a-input-number>
                    </a-space>
                </a-form-item>
            </div>

            <a-form-item label="保持页面尺寸">
                <a-switch v-model:checked="store.keep_size" />
            </a-form-item>
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
    CropPDFByBBOX,
    CropPDFByMargin,
    CropPDFByRectAnnots,
} from '../../../wailsjs/go/main/App';
import type { FormInstance } from 'ant-design-vue';
import type { Rule } from 'ant-design-vue/es/form';
import { MinusCircleOutlined, PlusOutlined, EllipsisOutlined } from '@ant-design/icons-vue';
import { handleOps } from "../data";
import { useCropState } from '../../store/crop';

export default defineComponent({
    components: {
        MinusCircleOutlined,
        PlusOutlined,
        EllipsisOutlined,
    },
    setup() {
        const formRef = ref<FormInstance>();
        const store = useCropState();
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
            formRef.value?.clearValidate();
            store.resetState();
        }
        // 提交表单
        const confirmLoading = ref<boolean>(false);
        async function submit() {
            confirmLoading.value = true;
            if (store.op === "margin") {
                let margin = [store.up, store.right, store.down, store.left];
                await handleOps(CropPDFByMargin, [store.input, store.output, margin, store.unit, store.keep_size, store.page]);
            }
            else if (store.op === "bbox") {
                let bbox = [store.up, store.left, store.down, store.right];
                await handleOps(CropPDFByBBOX, [store.input, store.output, bbox, store.unit, store.keep_size, store.page]);
            } else if (store.op === "annot") {
                await handleOps(CropPDFByRectAnnots, [store.input, store.output, store.keep_size, store.page]);
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