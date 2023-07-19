<template>
    <div>
        <a-form ref="formRef" style="border: 1px solid #dddddd; padding: 10px 0;border-radius: 10px;margin-right: 5vw;"
            :model="store" :label-col="{ span: 3 }" :wrapper-col="{ offset: 1, span: 18 }" :rules="rules" @finish="onFinish"
            @finishFailed="onFinishFailed">
            <a-form-item name="cracktype" label="破解类型">
                <a-radio-group button-style="solid" v-model:value="store.crack_type">
                    <a-radio-button value="PDF">PDF</a-radio-button>
                    <a-radio-button value="ZIP">压缩包</a-radio-button>
                    <a-radio-button value="md5">MD5</a-radio-button>
                </a-radio-group>
            </a-form-item>
            <div v-if="store.crack_type === 'PDF'">
                <a-form-item name="hash_type" label="哈希类型">
                    <a-select v-model:value="store.hash_type" style="width: 400px">
                        <a-select-option :value="10500">PDF 1.4 - 1.6 (Acrobat 5 - 8)</a-select-option>
                        <a-select-option :value="25400">PDF 1.4 - 1.6 (Acrobat 5 - 8) - user and owner
                            pass</a-select-option>
                        <a-select-option :value="10600">PDF 1.7 Level 3 (Acrobat 9)</a-select-option>
                        <a-select-option :value="10700">PDF 1.7 Level 8 (Acrobat 10 - 11)</a-select-option>
                    </a-select>
                </a-form-item>
            </div>
            <div v-if="store.crack_type === 'ZIP'">
                <a-form-item name="hash_type" label="哈希类型">
                    <a-select v-model:value="store.hash_type" style="width: 250px">
                        <a-select-option :value="11600">7-Zip</a-select-option>
                        <a-select-option :value="17220">PKZIP (Compressed Multi-File)</a-select-option>
                        <a-select-option :value="17200">PKZIP (Compressed)</a-select-option>
                        <a-select-option :value="17225">PKZIP (Mixed Multi-File)</a-select-option>
                        <a-select-option :value="17230">PKZIP (Mixed Multi-File Checksum-Only)</a-select-option>
                    </a-select>
                </a-form-item>
            </div>
            <a-form-item name="charset" label="字符集">
                <a-select v-model:value="store.charset" style="width: 250px">
                    <a-select-option value="l">小写字母[a-z]</a-select-option>
                    <a-select-option value="u">大写字母[A-Z]</a-select-option>
                    <a-select-option value="d">数字[0-9]</a-select-option>
                    <a-select-option value="h">小写16进制[0-9a-f]</a-select-option>
                    <a-select-option value="H">大写16进制[0-9A-F]</a-select-option>
                    <a-select-option value="s">特殊符号[!"#$等]</a-select-option>
                    <a-select-option value="a">大小写字母+数字+特殊符号</a-select-option>
                    <a-select-option value="b">0x00-0xff</a-select-option>
                </a-select>
            </a-form-item>
            <a-form-item name="attack_mode" label="攻击模式">
                <a-select v-model:value="store.attack_mode" style="width: 250px">
                    <a-select-option value="0">Straight</a-select-option>
                    <a-select-option value="1">Combination</a-select-option>
                    <a-select-option value="3">Brute-force</a-select-option>
                    <a-select-option value="6">Hybrid Wordlist + Mask</a-select-option>
                    <a-select-option value="7">Hybrid Mask + Wordlist</a-select-option>
                    <a-select-option value="9">Association</a-select-option>
                </a-select>
            </a-form-item>
            <a-form-item name="dict_path" label="字典库">
                <a-input v-model:value="store.dict_path" placeholder="输入字典库文件路径(留空则使用内置字典库)" allow-clear />
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
        <div style="margin-top: 1.2vh;width: 85%;">
            <a-alert message="本功能需要提前安装好hashcat。 下载地址：https://github.com/hashcat/hashcat/releases" type="info" show-icon />
        </div>
    </div>
</template>
<script lang="ts">
import { defineComponent, reactive, watch, ref } from 'vue';
import { message, Modal } from 'ant-design-vue';
import {
    CheckFileExists,
    CheckRangeFormat,
    SelectFile,
    SaveFile
} from '../../../wailsjs/go/main/App';
import type { FormInstance } from 'ant-design-vue';
import { EllipsisOutlined } from '@ant-design/icons-vue';
import type { Rule } from 'ant-design-vue/es/form';
import type { CrackState } from "../data";
import { handleOps } from "../data";
import { useCrackState } from '../../store/crack';

export default defineComponent({
    components: {
        EllipsisOutlined
    },
    setup() {
        const formRef = ref<FormInstance>();
        const store = useCrackState();
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
            store.resetState();
        }
        // 提交表单
        const confirmLoading = ref<boolean>(false);
        async function submit() {
            confirmLoading.value = true;
            // await handleOps(RotatePDF, [store.input, store.output, store.degree, store.page]);
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