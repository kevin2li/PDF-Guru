<template>
    <div>
        <a-form ref="formRef" style="border: 1px solid #dddddd; padding: 10px 0;border-radius: 10px;margin-right: 5vw;"
            :model="store" :label-col="{ span: 3 }" :wrapper-col="{ offset: 1, span: 18 }" :rules="rules" @finish="onFinish"
            @finishFailed="onFinishFailed">
            <a-form-item name="op" label="操作">
                <a-radio-group button-style="solid" v-model:value="store.op">
                    <a-radio-button value="remove">删除批注</a-radio-button>
                    <a-radio-button value="export" disabled>导出批注</a-radio-button>
                    <a-radio-button value="import" disabled>导入批注</a-radio-button>
                </a-radio-group>
            </a-form-item>
            <div v-if="store.op == 'remove'">
                <a-form-item label="删除类型">
                    <a-checkbox v-model:checked="checkAll" :indeterminate="indeterminate"
                        @change="onCheckAllChange">全选</a-checkbox>
                    <a-checkbox-group v-model:value="store.annot_types">
                        <a-divider />
                        <a-checkbox value="highlight">
                            <span>高亮</span>
                        </a-checkbox>
                        <a-checkbox value="underline">
                            <span>下划线</span>
                        </a-checkbox>
                        <a-checkbox value="squiggly">
                            <span>波浪线</span>
                        </a-checkbox>
                        <a-checkbox value="strikeout">
                            <span>删除线</span>
                        </a-checkbox>
                        <a-checkbox value="caret">
                            <span>插入/替换符</span>
                        </a-checkbox>
                        <a-checkbox value="text">
                            <span>文字批注</span>
                        </a-checkbox>
                        <a-checkbox value="textbox">
                            <span>文本框</span>
                        </a-checkbox>
                        <a-checkbox value="callout">
                            <span>指示批注</span>
                        </a-checkbox>
                        <a-checkbox value="popup">
                            <span>注解</span>
                        </a-checkbox>
                        <a-checkbox value="square">
                            <span>矩形</span>
                        </a-checkbox>
                        <a-checkbox value="oval">
                            <span>椭圆</span>
                        </a-checkbox>
                        <a-checkbox value="polygon">
                            <span>多边形</span>
                        </a-checkbox>
                        <a-checkbox value="cloud">
                            <span>云朵</span>
                        </a-checkbox>
                        <a-checkbox value="line">
                            <span>直线</span>
                        </a-checkbox>
                        <a-checkbox value="arrow">
                            <span>箭头</span>
                        </a-checkbox>
                        <a-checkbox value="polyline">
                            <span>自定义图形</span>
                        </a-checkbox>
                    </a-checkbox-group>
                </a-form-item>
            </div>

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
    AnnotParser,
} from '../../../wailsjs/go/main/App';
import type { FormInstance } from 'ant-design-vue';
import type { Rule } from 'ant-design-vue/es/form';
import { MinusCircleOutlined, PlusOutlined, EllipsisOutlined } from '@ant-design/icons-vue';
import { handleOps } from "../data";
import { useAnnotState } from "../../store/annot";

export default defineComponent({
    components: {
        MinusCircleOutlined,
        PlusOutlined,
        EllipsisOutlined
    },
    setup() {
        const formRef = ref<FormInstance>();
        const store = useAnnotState();
        // 多选框
        const indeterminate = ref<boolean>(false);
        const checkAll = ref<boolean>(false);
        const all_annot_types = [
            'highlight',
            'underline',
            'squiggly',
            'strikeout',
            'caret',
            'redact',
            'text',
            'textbox',
            'callout',
            'popup',
            'square',
            'oval',
            'polygon',
            'cloud',
            'line',
            'arrow',
            'polyline',
            "ink",
            "fileattachment",
        ];
        const onCheckAllChange = (e: any) => {
            Object.assign(store, {
                annot_types: e.target.checked ? all_annot_types : [],
            });
            indeterminate.value = false;
        };
        watch(
            () => store.annot_types,
            (val: any) => {
                indeterminate.value = !!val.length && val.length < all_annot_types.length;
                checkAll.value = val.length === all_annot_types.length;
            }
        )
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
            switch (store.op) {
                case "remove": {
                    if (checkAll.value) {
                        store.annot_types.push('all');
                    }
                    await handleOps(AnnotParser, [
                        store.input,
                        store.output,
                        store.op,
                        store.annot_types,
                        store.page,
                    ])
                    break;
                }
                case "export": {
                    break;
                }
                case "import": {
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
            resetFields,
            onFinish,
            onFinishFailed,
            onCheckAllChange,
            indeterminate,
            checkAll,
        };
    }
})
</script>