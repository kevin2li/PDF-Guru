<template>
    <div>
        <a-form ref="formRef" style="border: 1px solid #dddddd; padding: 10px 0;border-radius: 10px;margin-right: 5vw;"
            :model="formState" :label-col="{ span: 3 }" :wrapper-col="{ offset: 1, span: 18 }" :rules="rules"
            @finish="onFinish" @finishFailed="onFinishFailed">
            <a-form-item name="python_path" label="python路径" hasFeedback :validateStatus="validateStatus.python_path"
                :help="validateHelp.python_path">
                <a-input v-model:value="formState.python_path" placeholder="填写python路径" :disabled="!formState.allow_modify"
                    allow-clear></a-input>
            </a-form-item>
            <a-form-item name="tesseract_path" label="tesseract路径" hasFeedback :validateStatus="validateStatus.tesseract_path"
                :help="validateHelp.tesseract_path">
                <a-input v-model:value="formState.tesseract_path" placeholder="填写tesseract路径"
                    :disabled="!formState.allow_modify" allow-clear></a-input>
            </a-form-item>
            <a-form-item name="hashcat_path" label="hashcat路径" hasFeedback :validateStatus="validateStatus.hashcat_path"
                :help="validateHelp.hashcat_path">
                <a-input v-model:value="formState.hashcat_path" placeholder="填写hashcat路径" :disabled="!formState.allow_modify"
                    allow-clear></a-input>
            </a-form-item>
            <a-form-item name="pandoc_path" label="pandoc路径" hasFeedback :validateStatus="validateStatus.pandoc_path"
                :help="validateHelp.pandoc_path">
                <a-input v-model:value="formState.pandoc_path" placeholder="填写pandoc路径" :disabled="!formState.allow_modify"
                    allow-clear></a-input>
            </a-form-item>
            <a-form-item :wrapperCol="{ offset: 4 }" style="margin-bottom: 10px;">
                <a-button type="primary" html-type="submit" :loading="confirmLoading">{{ button_text }}
                </a-button>
            </a-form-item>
        </a-form>
        <div>
            <a-space direction="vertical">
                <div style="margin-top: 20px;">
                    项目地址：<a href="https://github.com/kevin2li/PDF-Guru"
                        target="_blank">https://github.com/kevin2li/PDF-Guru</a>
                </div>
                <div>
                    作者：<a href="https://github.com/kevin2li" target="_blank">Kevin2li</a>
                </div>
                <div>
                    B站：<a href="https://space.bilibili.com/369356107"
                        target="_blank">https://space.bilibili.com/369356107</a>
                </div>
            </a-space>
        </div>
        <a-divider></a-divider>
        <!-- <b>相关资源下载：</b>
        <div style="margin-top: 1vh;">
            <a-space direction="vertical">
                <div>1. Python: </div>
                <div>2. tesseract ocr: </div>
                <div>3. Pandoc: </div>
            </a-space>
        </div> -->
    </div>
</template>
<script lang="ts">
import { defineComponent, reactive, watch, ref, onMounted } from 'vue';
import { message, Modal } from 'ant-design-vue';
import { CheckFileExists, SaveConfig, LoadConfig } from '../../../wailsjs/go/main/App';
import type { FormInstance } from 'ant-design-vue';
import type { Rule } from 'ant-design-vue/es/form';
import type { PreferencesState } from "../data";
export default defineComponent({
    components: {
    },
    setup() {
        const formRef = ref<FormInstance>();
        const formState = reactive<PreferencesState>({
            pdf_path: "",
            python_path: "",
            tesseract_path: "",
            pandoc_path: "",
            hashcat_path: "",
            allow_modify: false,
        });
        const button_text = ref("修改");
        const validateStatus = reactive({
            python_path: "",
            pandoc_path: "",
            tesseract_path: "",
            hashcat_path: "",
        });
        const validateHelp = reactive({
            python_path: "",
            pandoc_path: "",
            tesseract_path: "",
            hashcat_path: "",
        });
        const loadConfig = async () => {
            await LoadConfig().then((res: any) => {
                console.log({ res });
                formState.pdf_path = res.pdf_path;
                formState.python_path = res.python_path;
                formState.tesseract_path = res.tesseract_path;
                formState.pandoc_path = res.pandoc_path;
            }).catch((err: any) => {
                console.log({ err });
                message.error("加载配置失败");
            });
        }
        const validateFileExists = async (_rule: Rule, value: string) => {
            // @ts-ignore
            validateStatus[_rule.field] = 'validating';
            if (value.trim() === "") {
                // @ts-ignore
                validateStatus[_rule.field] = '';
                // @ts-ignore
                validateHelp[_rule.field] = '';
                return Promise.resolve();
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
        };

        const rules: Record<string, Rule[]> = {
            python_path: [{ validator: validateFileExists, trigger: 'change' }],
            pandoc_path: [{ validator: validateFileExists, trigger: 'change' }],
            tesseract_path: [{ validator: validateFileExists, trigger: 'change' }],
            hashcat_path: [{ validator: validateFileExists, trigger: 'change' }],
        };
        // 重置表单
        const resetFields = () => {
            formRef.value?.resetFields();
        }
        // 提交表单
        const confirmLoading = ref<boolean>(false);
        const submit = async () => {
            confirmLoading.value = true;
            formState.allow_modify = !formState.allow_modify;
            button_text.value = formState.allow_modify ? "保存" : "修改";
            if (!formState.allow_modify) {
                await SaveConfig(formState.pdf_path, formState.python_path, formState.tesseract_path, formState.pandoc_path, formState.hashcat_path).then((res: any) => {
                    console.log({ res });
                    message.success("保存成功");
                }).catch((err: any) => {
                    console.log({ err });
                    message.error("保存失败");
                });
            }
            formRef.value?.clearValidate();
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

        onMounted(async () => {
            await loadConfig();
        });
        return { formState, rules, formRef, validateStatus, validateHelp, confirmLoading, button_text, resetFields, onFinish, onFinishFailed };
    }
})
</script>