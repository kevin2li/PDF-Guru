<template>
    <div>
        <a-form ref="formRef" style="border: 1px solid #dddddd; padding: 10px 0;border-radius: 10px;margin-right: 5vw;"
            :model="store" :label-col="{ span: 3 }" :wrapper-col="{ offset: 1, span: 18 }" :rules="rules" @finish="onFinish"
            @finishFailed="onFinishFailed">
            <a-form-item name="op" label="操作" style="margin-bottom: 1.8vh;">
                <a-radio-group button-style="solid" v-model:value="store.op">
                    <a-radio-button value="encrypt">添加密码</a-radio-button>
                    <a-radio-button value="decrypt">移除密码</a-radio-button>
                    <a-radio-button value="change">修改密码</a-radio-button>
                    <a-radio-button value="recover">恢复权限</a-radio-button>
                </a-radio-group>
            </a-form-item>
            <div v-if="store.op == 'encrypt'">
                <div style="border: 1px solid #dddddd;border-radius: 10px;margin: 0 1vw;">
                    <a-form-item name="is_set_upw" label="设置打开密码" :disabled="!store.is_set_upw">
                        <a-checkbox v-model:checked="store.is_set_upw"></a-checkbox>
                    </a-form-item>
                    <a-form-item :name="store.is_set_upw ? 'upw' : 'upw-none'" label="设置密码" hasFeedback
                        :validateStatus="validateStatus.encrypt_upw">
                        <a-input-password v-model:value="store.upw" placeholder="不少于6位" allow-clear
                            :disabled="!store.is_set_upw" />
                    </a-form-item>
                    <a-form-item :name="store.is_set_upw ? 'upw_confirm' : 'upw_confirm-none'" label="确认密码" hasFeedback
                        :validateStatus="validateStatus.encrypt_upw_confirm">
                        <a-input-password v-model:value="store.upw_confirm" placeholder="再次输入密码" allow-clear
                            :disabled="!store.is_set_upw" />
                    </a-form-item>
                </div>
                <div style="border: 1px solid #dddddd;border-radius: 10px;margin: 1vw 1vw;">
                    <a-form-item name="is_set_opw" label="设置权限密码">
                        <a-checkbox v-model:checked="store.is_set_opw"></a-checkbox>
                    </a-form-item>
                    <a-form-item :name="store.is_set_opw ? 'opw' : 'opw-none'" label="设置密码" hasFeedback
                        :validateStatus="validateStatus.encrypt_opw">
                        <a-input-password v-model:value="store.opw" placeholder="不少于6位" allow-clear
                            :disabled="!store.is_set_opw" />
                    </a-form-item>
                    <a-form-item :name="store.is_set_opw ? 'opw_confirm' : 'opw_confirm-none'" label="确认密码" hasFeedback
                        :validateStatus="validateStatus.encrypt_opw_confirm">
                        <a-input-password v-model:value="store.opw_confirm" allow-clear placeholder="再次输入密码"
                            :disabled="!store.is_set_opw" />
                    </a-form-item>
                    <a-form-item :name="store.is_set_opw ? 'perm' : 'perm-none'" label="保护功能">
                        <a-checkbox v-model:checked="checkAll" :indeterminate="indeterminate" :disabled="!store.is_set_opw"
                            @change="onCheckAllChange">全选</a-checkbox>
                        <a-divider type="vertical" />
                        <a-checkbox-group v-model:value="store.perm" :options="encrypt_perm_options"
                            :disabled="!store.is_set_opw" />
                    </a-form-item>
                </div>
            </div>
            <div v-if="store.op == 'decrypt'">
                <a-form-item name="upw" label="密码" :rules="[{
                    required: true, message: '请填写密码'
                }]">
                    <a-input-password v-model:value="store.upw" placeholder="解密密码" allow-clear />
                </a-form-item>
            </div>
            <div v-if="store.op === 'change'">
                <div style="border: 1px solid #dddddd;border-radius: 10px;margin: 0 1vw;">
                    <a-form-item label="修改打开密码">
                        <a-checkbox v-model:checked="store.is_set_upw"></a-checkbox>
                    </a-form-item>
                    <a-form-item :name="store.is_set_upw ? 'old_upw' : 'old_upw-none'" label="旧打开密码">
                        <a-input-password v-model:value="store.old_upw" placeholder="请输入旧密码" allow-clear
                            :disabled="!store.is_set_upw" />
                    </a-form-item>
                    <a-form-item :name="store.is_set_upw ? 'upw' : 'upw-none'" label="新打开密码">
                        <a-input-password v-model:value="store.upw" placeholder="请输入打开密码" allow-clear
                            :disabled="!store.is_set_upw" />
                    </a-form-item>
                </div>
                <div style="border: 1px solid #dddddd;border-radius: 10px;margin: 1vh 1vw;">
                    <a-form-item label="修改权限密码">
                        <a-checkbox v-model:checked="store.is_set_opw"></a-checkbox>
                    </a-form-item>
                    <a-form-item :name="store.is_set_opw ? 'old_opw' : 'old_opw-none'" label="旧权限密码">
                        <a-input-password v-model:value="store.old_opw" placeholder="请输入旧密码" allow-clear
                            :disabled="!store.is_set_opw" />
                    </a-form-item>
                    <a-form-item :name="store.is_set_opw ? 'opw' : 'opw-none'" label="新权限密码">
                        <a-input-password v-model:value="store.opw" placeholder="请输入权限密码" allow-clear
                            :disabled="!store.is_set_opw" />
                    </a-form-item>
                </div>
            </div>
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
                            <a-input v-model:value="store.output" placeholder="输出目录(留空则保存到输入文件同级目录)" allow-clear />
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
    EncryptPDF,
    DecryptPDF,
    ChangePasswordPDF,
} from '../../../wailsjs/go/main/App';
import type { FormInstance } from 'ant-design-vue';
import { EllipsisOutlined } from '@ant-design/icons-vue';
import type { Rule } from 'ant-design-vue/es/form';
import { handleOps } from "../data";
import { useEncryptState } from '../../store/encrypt';

export default defineComponent({
    components: {
        EllipsisOutlined
    },
    setup() {
        const formRef = ref<FormInstance>();
        const store = useEncryptState();

        const validateStatus = reactive({
            input: "",
            encrypt_upw: '',
            encrypt_upw_confirm: '',
            encrypt_opw: '',
            encrypt_opw_confirm: '',
            old_upw: '',
            old_opw: '',
        });
        const validateHelp = reactive({
            input: "",
            encrypt_upw: '',
            encrypt_upw_confirm: '',
            encrypt_opw: '',
            encrypt_opw_confirm: '',
            old_upw: '',
            old_opw: '',
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
        let validatePassUpw = async (_rule: Rule, value: string) => {
            validateStatus["encrypt_upw"] = 'validating';
            if (value === '') {
                validateStatus["encrypt_upw"] = 'error';
                return Promise.reject('请输入密码');
            } else {
                if (value.length < 6) {
                    validateStatus["encrypt_upw"] = 'error';
                    return Promise.reject('密码长度不能少于6位');
                }
                validateStatus["encrypt_upw"] = 'success';
                return Promise.resolve();
            }
        };
        let validatePassOpw = async (_rule: Rule, value: string) => {
            validateStatus["encrypt_opw"] = 'validating';
            if (value === '') {
                validateStatus["encrypt_opw"] = 'error';
                return Promise.reject('请输入密码');
            } else {
                if (value.length < 6) {
                    validateStatus["encrypt_opw"] = 'error';
                    return Promise.reject('密码长度不能少于6位');
                }
                validateStatus["encrypt_opw"] = 'success';
                return Promise.resolve();
            }
        };

        let validatePassUpwConfirm = async (_rule: Rule, value: string) => {
            validateStatus.encrypt_upw_confirm = 'validating';
            if (value === '') {
                validateStatus.encrypt_upw_confirm = 'error';
                return Promise.reject('请再次输入密码');
            } else if (value !== store.upw) {
                validateStatus.encrypt_upw_confirm = 'error';
                return Promise.reject("两次密码输入不一致");
            } else {
                validateStatus.encrypt_upw_confirm = 'success';
                return Promise.resolve();
            }
        };
        let validatePassOpwConfirm = async (_rule: Rule, value: string) => {
            validateStatus.encrypt_opw_confirm = 'validating';
            if (value === '') {
                validateStatus.encrypt_opw_confirm = 'error';
                return Promise.reject('请再次输入密码');
            } else if (value !== store.opw) {
                validateStatus.encrypt_opw_confirm = 'error';
                return Promise.reject("两次密码输入不一致");
            } else {
                validateStatus.encrypt_opw_confirm = 'success';
                return Promise.resolve();
            }
        };

        const rules: Record<string, Rule[]> = {
            input: [{ required: true, validator: validateFileExists, trigger: 'change', message: '文件不存在' }],
            perm: [{ required: true, type: 'array', min: 1, message: '请至少选择一项' }],
            upw: [{ required: true, validator: validatePassUpw, trigger: 'change' }],
            upw_confirm: [{ required: true, validator: validatePassUpwConfirm, trigger: 'change' }],
            opw: [{ required: true, validator: validatePassOpw, trigger: 'change' }],
            opw_confirm: [{ required: true, validator: validatePassOpwConfirm, trigger: 'change' }],
            old_upw: [{ required: true, validator: validatePassUpw, trigger: 'change' }],
            old_opw: [{ required: true, validator: validatePassOpw, trigger: 'change' }],
        };
        // 多选框
        const indeterminate = ref<boolean>(false);
        const checkAll = ref<boolean>(false);
        const encrypt_perm_options = [
            "复制", "注释", "打印", "表单", "插入/删除页面"
        ];
        const onCheckAllChange = (e: any) => {
            Object.assign(store, {
                perm: e.target.checked ? encrypt_perm_options : [],
            });
            indeterminate.value = false;
        };
        watch(
            () => store.perm,
            (val: any) => {
                indeterminate.value = !!val.length && val.length < encrypt_perm_options.length;
                checkAll.value = val.length === encrypt_perm_options.length;
            }
        )
        // 重置表单
        const resetFields = () => {
            formRef.value?.clearValidate();
            store.resetState();
        }
        // 提交表单
        const confirmLoading = ref<boolean>(false);
        async function submit() {
            if (store.op === 'encrypt' && !store.is_set_opw && !store.is_set_upw) {
                message.error("请至少设置一种密码");
                return;
            }
            confirmLoading.value = true;
            switch (store.op) {
                case "encrypt": {
                    let upw = "", opw = "", perm: string[] = [];
                    if (store.is_set_upw) {
                        upw = store.upw;
                        perm = ["打开"];
                    }
                    if (store.is_set_opw) {
                        opw = store.opw;
                        perm = store.perm;
                        if (!perm.includes("打开")) {
                            perm.push("打开");
                        }
                    }
                    await handleOps(EncryptPDF, [store.input, store.output, upw, opw, perm]);
                    break;
                }
                case "decrypt": {
                    await handleOps(DecryptPDF, [store.input, store.output, store.upw]);
                    break;
                }
                case "change": {
                    let old_upw = "", upw = "", old_opw = "", opw = "";
                    if (store.is_set_upw) {
                        old_upw = store.old_upw;
                        upw = store.upw;
                    }
                    if (store.is_set_opw) {
                        old_opw = store.old_opw;
                        opw = store.opw;
                    }
                    await handleOps(ChangePasswordPDF, [store.input, store.output, old_upw, upw, old_opw, opw])
                    break;
                }
                case "recover": {
                    await handleOps(DecryptPDF, [store.input, store.output, ""]);
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
            checkAll,
            indeterminate,
            encrypt_perm_options,
            onCheckAllChange,
            resetFields,
            onFinish,
            onFinishFailed
        };
    }
})
</script>