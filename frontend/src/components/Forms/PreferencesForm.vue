<template>
    <div>
        <a-form ref="formRef" style="border: 1px solid #dddddd; padding: 10px 0;border-radius: 10px;margin-right: 5vw;"
            :model="formState" :label-col="{ span: 3 }" :wrapper-col="{ offset: 1, span: 18 }" :rules="rules"
            @finish="onFinish" @finishFailed="onFinishFailed">
            <a-form-item name="python_path" label="python路径" :validateStatus="validateStatus.python_path"
                :help="validateHelp.python_path">
                <div>
                    <a-row>
                        <a-col :span="22">
                            <a-input v-model:value="formState.python_path" placeholder="填写python路径"
                                :disabled="!formState.allow_modify" allow-clear></a-input>
                        </a-col>
                        <a-col :span="1" style="margin-left: 1vw;">
                            <a-tooltip>
                                <template #title>选择文件</template>
                                <a-button @click="selectFile('python_path')"
                                    v-if="formState.allow_modify"><ellipsis-outlined /></a-button>
                            </a-tooltip>
                        </a-col>
                    </a-row>
                </div>
            </a-form-item>
            <a-form-item name="tesseract_path" label="tesseract路径" :validateStatus="validateStatus.tesseract_path"
                :help="validateHelp.tesseract_path">
                <div>
                    <a-row>
                        <a-col :span="22">
                            <a-input v-model:value="formState.tesseract_path" placeholder="填写tesseract路径"
                                :disabled="!formState.allow_modify" allow-clear></a-input>
                        </a-col>
                        <a-col :span="1" style="margin-left: 1vw;">
                            <a-tooltip>
                                <template #title>选择文件</template>
                                <a-button @click="selectFile('tesseract_path')"
                                    v-if="formState.allow_modify"><ellipsis-outlined /></a-button>
                            </a-tooltip>
                        </a-col>
                    </a-row>
                </div>
            </a-form-item>
            <!-- <a-form-item name="hashcat_path" label="hashcat路径" :validateStatus="validateStatus.hashcat_path"
                :help="validateHelp.hashcat_path">
                <div>
                    <a-row>
                        <a-col :span="22">
                            <a-input v-model:value="formState.hashcat_path" placeholder="填写hashcat路径"
                                :disabled="!formState.allow_modify" allow-clear></a-input>
                        </a-col>
                        <a-col :span="1" style="margin-left: 1vw;">
                            <a-tooltip>
                                <template #title>选择文件</template>
                                <a-button @click="selectFile('hashcat_path')"
                                    v-if="formState.allow_modify"><ellipsis-outlined /></a-button>
                            </a-tooltip>
                        </a-col>
                    </a-row>
                </div>
            </a-form-item> -->
            <a-form-item name="pandoc_path" label="pandoc路径" :validateStatus="validateStatus.pandoc_path"
                :help="validateHelp.pandoc_path">
                <div>
                    <a-row>
                        <a-col :span="22">
                            <a-input v-model:value="formState.pandoc_path" placeholder="填写pandoc路径"
                                :disabled="!formState.allow_modify" allow-clear></a-input>
                        </a-col>
                        <a-col :span="1" style="margin-left: 1vw;">
                            <a-tooltip>
                                <template #title>选择文件</template>
                                <a-button @click="selectFile('pandoc_path')"
                                    v-if="formState.allow_modify"><ellipsis-outlined /></a-button>
                            </a-tooltip>
                        </a-col>
                    </a-row>
                </div>
            </a-form-item>
            <a-form-item :wrapperCol="{ offset: 4 }" style="margin-bottom: 10px;">
                <a-button type="primary" html-type="submit" :loading="confirmLoading">{{ button_text }}
                </a-button>
            </a-form-item>
        </a-form>
        <div>
            <a-form :label-col="{ span: 2 }" :wrapper-col="{ offset: 0, span: 18 }" style="margin-top: 20px;">
                <a-form-item label="Github地址">
                    <a-button type="link" @click="OpenUrl('https://github.com/kevin2li/PDF-Guru')">
                        <github-outlined />
                        https://github.com/kevin2li/PDF-Guru
                    </a-button>
                </a-form-item>
                <a-form-item label="作者" style="margin-top: -20px;">
                    <a-button type="link" @click="OpenUrl('https://github.com/kevin2li')">
                        <user-outlined />
                        Kevin2li
                    </a-button>
                </a-form-item>
                <a-form-item label="Gitee地址" style="margin-top: -20px;">
                    <a-button type="link" @click="OpenUrl('https://gitee.com/Kevin234/PDF-Guru')">
                        https://gitee.com/Kevin234/PDF-Guru
                    </a-button>
                </a-form-item>
                <a-form-item label="B站" style="margin-top: -20px;">
                    <a-button type="link" @click="OpenUrl('https://space.bilibili.com/369356107')">
                        https://space.bilibili.com/369356107
                    </a-button>
                </a-form-item>
            </a-form>
        </div>
        <a-divider></a-divider>
        <div>
        </div>
        <!-- <a-space>  
            <a-button @click="selectFile" type="primary">测试选择文件</a-button>
            <a-button @click="selectMultipleFiles" type="primary">测试选择多文件</a-button>
            <a-button @click="selectDir" type="primary">测试选择目录</a-button>
        </a-space> -->
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
import {
    CheckFileExists,
    SaveConfig,
    LoadConfig,
    SelectFile,
    SaveFile,
    SelectDir,
    SelectMultipleFiles,
    OpenUrl,
    GetClipboard,
} from '../../../wailsjs/go/main/App';
import type { FormInstance } from 'ant-design-vue';
import type { Rule } from 'ant-design-vue/es/form';
import { EllipsisOutlined, GithubOutlined, UserOutlined } from '@ant-design/icons-vue';
import type { PreferencesState } from "../data";
export default defineComponent({
    components: {
        EllipsisOutlined,
        GithubOutlined,
        UserOutlined
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
                // message.error("加载配置失败");
                Modal.error({
                    title: "加载配置失败",
                    content: err,
                })
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
            formRef.value?.clearValidate();
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
                    // message.error("保存失败");
                    Modal.error({
                        title: "保存失败",
                        content: err,
                    })
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
        const handleMouseButtonDown = async (e: any) => {
            console.log({ e });
            if (e.button === 2) {
                // 右键
                console.log("中键");
                await GetClipboard().then((res: any) => {
                    console.log({ res });
                    // if (res) {
                    //     Object.assign(formState, { [e.target.name]: res });
                    // }
                    // formRef.value?.validateFields(e.target.name);
                }).catch((err: any) => {
                    console.log({ err });
                });
                e.preventDefault();
                e.stopPropagation();
                return false;
            }
        }

        onMounted(async () => {
            await loadConfig();
            window.addEventListener("mousedown", handleMouseButtonDown);
        });
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
        const selectMultipleFiles = async () => {
            await SelectMultipleFiles().then((res: any) => {
                console.log({ res });
            }).catch((err: any) => {
                console.log({ err });
            });
        }
        const selectDir = async () => {
            await SelectDir().then((res: any) => {
                console.log({ res });
            }).catch((err: any) => {
                console.log({ err });
            });
        }
        return {
            formState,
            rules,
            formRef,
            validateStatus,
            validateHelp,
            confirmLoading,
            button_text,
            resetFields,
            onFinish,
            onFinishFailed,
            selectFile,
            saveFile,
            selectMultipleFiles,
            selectDir,
            OpenUrl,
        };
    }
})
</script>