<template>
    <div>
        <a-form ref="formRef" style="border: 1px solid #dddddd; padding: 10px 0;border-radius: 10px;margin-right: 5vw;"
            :model="formState" :label-col="{ span: 3 }" :wrapper-col="{ offset: 1, span: 18 }" :rules="rules"
            @finish="onFinish" @finishFailed="onFinishFailed">
            <a-form-item name="input" label="输入" :validateStatus="validateStatus.input" :help="validateHelp.input">
                <div>
                    <a-row>
                        <a-col :span="22">
                            <a-input v-model:value="formState.input" placeholder="输入文件路径, 支持使用*匹配多个文件, 如D:\test\*.pdf" allow-clear />
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
            <a-form-item :wrapperCol="{ offset: 4 }" style="margin-bottom: 10px;">
                <a-button type="primary" html-type="submit" :loading="confirmLoading">确认</a-button>
                <a-button style="margin-left: 10px" @click="resetFields">重置</a-button>
            </a-form-item>
        </a-form>
        <a-divider></a-divider>
        <div>
            <a-typography-title :level="3">结果：</a-typography-title>
        </div>
        <div style="margin-top: 1.5vh;">
            <a-tabs v-model:activatekey="formState.activeKey" type="card">
                <a-tab-pane key="1" tab="基本信息" class="tab">
                    <div>
                        <a-form :label-col="{ span: 3 }">
                            <a-row>
                                <a-col :span="12">
                                    <a-form-item label="PDF版本">
                                        <div>xxx</div>
                                    </a-form-item>
                                    <a-form-item label="总页数">
                                        <div>xxx</div>
                                    </a-form-item>
                                    <a-form-item label="页面大小">
                                        <div>xxx</div>
                                    </a-form-item>
                                    <a-form-item label="文件大小">
                                        <div>xxx</div>
                                    </a-form-item>
                                    <a-form-item label="创建时间">
                                        <div>xxx</div>
                                    </a-form-item>
                                    <a-form-item label="修改时间">
                                        <div>xxx</div>
                                    </a-form-item>
                                    <a-form-item label="是否加密">
                                        <div>xxx</div>
                                    </a-form-item>
                                </a-col>
                                <a-col :span="12">
                                    <a-form-item label="标题">
                                        <div>xxx</div>
                                    </a-form-item>
                                    <a-form-item label="作者">
                                        <div>xxx</div>
                                    </a-form-item>
                                    <a-form-item label="主题">
                                        <div>xxx</div>
                                    </a-form-item>
                                    <a-form-item label="关键字">
                                        <div>xxx</div>
                                    </a-form-item>
                                    <a-form-item label="创建程序">
                                        <div>xxx</div>
                                    </a-form-item>
                                    <a-form-item label="制作工具">
                                        <div>xxx</div>
                                    </a-form-item>
                                </a-col>
                            </a-row>
                        </a-form>
                    </div>
                </a-tab-pane>
                <a-tab-pane key="2" tab="安全性" class="tab">
                    <div>
                        <a-form :label-col="{ span: 3 }">
                            <div>
                                <b>安全性：</b>
                            </div>
                            <a-form-item label="安全方法">
                                <div>无保护</div>
                            </a-form-item>
                            <div>
                                <b>文档权限：</b>
                            </div>
                            <a-form-item label="打印">
                                <div>允许</div>
                            </a-form-item>
                            <a-form-item label="复制">
                                <div>允许</div>
                            </a-form-item>
                            <a-form-item label="注释">
                                <div>允许</div>
                            </a-form-item>
                            <a-form-item label="填写表单">
                                <div>允许</div>
                            </a-form-item>
                            <a-form-item label="页面提取">
                                <div>允许</div>
                            </a-form-item>
                            <a-form-item label="文档组合">
                                <div>允许</div>
                            </a-form-item>
                        </a-form>
                    </div>
                </a-tab-pane>
                <a-tab-pane key="3" tab="字体" class="tab">

                </a-tab-pane>
            </a-tabs>

        </div>
    </div>
</template>
<script lang="ts">
import { defineComponent, reactive, watch, ref } from 'vue';
import { message, Modal } from 'ant-design-vue';
import {
    SelectFile,
    SaveFile,
    CheckFileExists,
    CheckRangeFormat
} from '../../../wailsjs/go/main/App';
import type { FormInstance } from 'ant-design-vue';
import { EllipsisOutlined } from '@ant-design/icons-vue';
import type { Rule } from 'ant-design-vue/es/form';
import { handleOps } from "../data";
export default defineComponent({
    components: {
        EllipsisOutlined
    },
    setup() {
        const formRef = ref<FormInstance>();
        const formState = reactive({
            input: "",
            activeKey: "1",
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
            formRef.value?.clearValidate();
        }
        // 提交表单
        const confirmLoading = ref<boolean>(false);
        async function submit() {
            confirmLoading.value = true;

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
            resetFields, onFinish, onFinishFailed
        };
    }
})
</script>
<style scoped>
.tab {
    border: 1px solid #dddddd;
    padding: 10px;
    border-radius: 10px;
    width: 85%;
}
</style>