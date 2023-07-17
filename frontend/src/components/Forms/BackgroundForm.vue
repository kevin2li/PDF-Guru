<template>
    <div>
        <a-form ref="formRef" style="border: 1px solid #dddddd; padding: 10px 0;border-radius: 10px;margin-right: 5vw;"
            :model="formState" :label-col="{ span: 3 }" :wrapper-col="{ offset: 1, span: 18 }" :rules="rules"
            @finish="onFinish" @finishFailed="onFinishFailed">
            <a-form-item name="op" label="背景填充">
                <a-radio-group v-model:value="formState.op">
                    <a-radio value="color">颜色</a-radio>
                    <a-radio value="image">图片</a-radio>
                </a-radio-group>
            </a-form-item>
            <a-form-item name="color" label="颜色" v-if="formState.op === 'color'" hasFeedback
                :validateStatus="validateStatus.color" :help="validateHelp.color">
                <a-input v-model:value="formState.color" style="width:300px" placeholder="颜色16进制码, e.g. #FF0000"
                    allow-clear />
                <a
                    :style="{ background: formState.color, border: '1px solid black', marginLeft: '20px' }">&nbsp;&nbsp;&nbsp;&nbsp;</a>
            </a-form-item>
            <a-form-item name="image_path" label="图片" v-if="formState.op === 'image'" hasFeedback
                :validateStatus="validateStatus.image_path" :help="validateHelp.image_path">
                <a-input v-model:value="formState.image_path" placeholder="图片路径" allow-clear />
            </a-form-item>
            <a-form-item name="watermark_font_opacity" label="外观">
                <a-space size="large">
                    <a-input-number v-model:value="formState.opacity" :min="0" :max="1" :step="0.01" style="width: 200px;">
                        <template #addonBefore>
                            不透明度
                        </template>
                    </a-input-number>
                    <div style="width: 100px;">
                        <a-slider v-model:value="formState.opacity" :min="0" :max="1" :step="0.01" />
                    </div>
                    <a-input-number v-model:value="formState.degree" :min="0" :max="360">
                        <template #addonBefore>
                            旋转角度
                        </template>
                    </a-input-number>
                    <a-input-number v-model:value="formState.scale" :min="0">
                        <template #addonBefore>
                            缩放比例
                        </template>
                    </a-input-number>
                </a-space>
            </a-form-item>
            <a-form-item label="位置">
                <a-space size="large">
                    <a-input-number v-model:value="formState.x_offset">
                        <template #addonBefore>
                            水平偏移量
                        </template>
                    </a-input-number>
                    <a-input-number v-model:value="formState.y_offset">
                        <template #addonBefore>
                            垂直偏移量
                        </template>
                    </a-input-number>
                </a-space>
            </a-form-item>
            <a-form-item name="page" hasFeedback :validateStatus="validateStatus.page" :help="validateHelp.page"
                label="页码范围">
                <a-input v-model:value="formState.page" placeholder="应用的页码范围(留空表示全部), e.g. 1-10" allow-clear />
            </a-form-item>
            <a-form-item name="input" label="输入" :validateStatus="validateStatus.input" :help="validateHelp.input">
                <div>
                    <a-row>
                        <a-col :span="22">
                            <a-input v-model:value="formState.input" placeholder="输入文件路径, 支持使用*匹配多个文件" allow-clear />
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
    AddPDFBackgroundByColor,
    AddPDFBackgroundByImage
} from '../../../wailsjs/go/main/App';
import type { FormInstance } from 'ant-design-vue';
import type { Rule } from 'ant-design-vue/es/form';
import { EllipsisOutlined } from '@ant-design/icons-vue';
import type { BackgroundState } from "../data";
import { handleOps } from "../data";
export default defineComponent({
    components: {
        EllipsisOutlined
    },
    setup() {
        const formRef = ref<FormInstance>();
        const formState = reactive<BackgroundState>({
            input: "",
            output: "",
            page: "",
            degree: 0,
            op: 'color',
            color: '#FFFFFF',
            opacity: 1,
            scale: 1,
            x_offset: 0,
            y_offset: 0,
            image_path: ''
        });

        const validateStatus = reactive({
            input: "",
            page: "",
            image_path: "",
            color: "",
        });
        const validateHelp = reactive({
            input: "",
            page: "",
            image_path: "",
            color: "",
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
        const validateImageFileExists = async (_rule: Rule, value: string) => {
            validateStatus["image_path"] = 'validating';
            if (value === '') {
                validateStatus["image_path"] = 'error';
                validateHelp["image_path"] = "请填写路径";
                return Promise.reject();
            }
            await CheckFileExists(value).then((res: any) => {
                console.log({ res });
                if (res) {
                    validateStatus["image_path"] = 'error';
                    validateHelp["image_path"] = res;
                    return Promise.reject();
                }
                validateStatus["image_path"] = 'success';
                validateHelp["image_path"] = '';
                return Promise.resolve();
            }).catch((err: any) => {
                console.log({ err });
                validateStatus["image_path"] = 'error';
                validateHelp["image_path"] = err;
                return Promise.reject();
            });
            const legal_suffix = [".png", ".jpg", ".jpeg", ".bmp", ".gif", "JPG", "PNG", "JPEG", "BMP", "GIF"];
            if (!legal_suffix.some((suffix) => value.trim().endsWith(suffix))) {
                validateStatus["image_path"] = 'error';
                validateHelp["image_path"] = "仅支持图片格式的文件";
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
        const validateHexColor = async (_rule: Rule, value: string) => {
            validateStatus["color"] = 'validating';
            if (value.trim() === '') {
                validateStatus["color"] = 'error';
                validateHelp["color"] = "请填写颜色";
                return Promise.reject();
            }
            const reg = /^#[0-9a-fA-f]{6}$/;
            if (!reg.test(value)) {
                validateStatus["color"] = 'error';
                validateHelp["color"] = "请填写正确的颜色";
                return Promise.reject();
            }
            validateStatus["color"] = 'success';
            validateHelp["color"] = '';
            return Promise.resolve();
        };
        const rules: Record<string, Rule[]> = {
            input: [{ required: true, validator: validateFileExists, trigger: 'change' }],
            image_path: [{ required: true, validator: validateImageFileExists, trigger: 'change' }],
            page: [{ validator: validateRange, trigger: 'change' }],
            color: [{ required: true, validator: validateHexColor, trigger: 'change' }]
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
                case 'color': {
                    await handleOps(AddPDFBackgroundByColor, [
                        formState.input,
                        formState.output,
                        formState.color,
                        formState.opacity,
                        formState.degree,
                        formState.x_offset,
                        formState.y_offset,
                        formState.page,
                    ]);
                    break;
                }
                case 'image': {
                    await handleOps(AddPDFBackgroundByImage, [
                        formState.input,
                        formState.image_path,
                        formState.output,
                        formState.opacity,
                        formState.degree,
                        formState.x_offset,
                        formState.y_offset,
                        formState.scale,
                        formState.page,
                    ]);
                }
                default:
                    break;
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
        const saveFile = async (field: string) => {
            await SaveFile().then((res: string) => {
                console.log({ res });
                if (res) {
                    Object.assign(formState, { [field]: res });
                }
                formRef.value?.validateFields(field);
            }).catch((err: any) => {
                console.log({ err });
            });
        }
        return {
            selectFile,
            saveFile,
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