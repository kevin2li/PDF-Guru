<template>
    <div>
        <a-form ref="formRef" style="border: 1px solid #dddddd; padding: 10px 0;border-radius: 10px;margin-right: 5vw;"
            :model="formState" :label-col="{ span: 3 }" :wrapper-col="{ offset: 1, span: 18 }" :rules="rules">
            <a-form-item name="crop_op" label="操作">
                <a-radio-group button-style="solid" v-model:value="formState.op">
                    <a-radio-button value="crop">裁剪</a-radio-button>
                    <a-radio-button value="split">分割</a-radio-button>
                </a-radio-group>
            </a-form-item>
            <a-form-item label="单位" v-if="formState.op == 'crop'">
                <a-radio-group v-model:value="formState.unit">
                    <a-radio value="cm">厘米</a-radio>
                    <a-radio value="mm">毫米</a-radio>
                    <a-radio value="px">像素</a-radio>
                    <a-radio value="in">英寸</a-radio>
                </a-radio-group>
            </a-form-item>
            <a-form-item name="crop.type" label="页边距" v-if="formState.op == 'crop'">
                <a-space size="large">
                    <a-input-number v-model:value="formState.up" :min="0">
                        <template #addonBefore>
                            上
                        </template>
                    </a-input-number>
                    <a-input-number v-model:value="formState.left" :min="0">
                        <template #addonBefore>
                            左
                        </template>
                    </a-input-number>
                    <a-input-number v-model:value="formState.down" :min="0">
                        <template #addonBefore>
                            下
                        </template>
                    </a-input-number>
                    <a-input-number v-model:value="formState.right" :min="0">
                        <template #addonBefore>
                            右
                        </template>
                    </a-input-number>
                </a-space>
            </a-form-item>
            <a-form-item label="分割类型" v-if="formState.op == 'split'">
                <a-radio-group v-model:value="formState.split_type">
                    <a-radio value="even">均匀分割</a-radio>
                    <a-radio value="custom">自定义分割</a-radio>
                </a-radio-group>
            </a-form-item>
            <a-form-item label="网格形状" v-if="formState.op == 'split' && formState.split_type == 'even'">
                <a-space size="large">
                    <a-input-number v-model:value="formState.split_rows" :min="1">
                        <template #addonBefore>
                            行数
                        </template>
                    </a-input-number>
                    <a-input-number v-model:value="formState.split_cols" :min="1">
                        <template #addonBefore>
                            列数
                        </template>
                    </a-input-number>
                </a-space>
            </a-form-item>
            <a-form-item :label="index === 0 ? '水平分割线' : ' '" :colon="index === 0 ? true : false"
                v-if="formState.op == 'split' && formState.split_type == 'custom'"
                v-for="(item, index) in formState.split_h_breakpoints" :key="index">
                <a-input-number :min="0" :max="100" :formatter="(value: any) => `${value}%`"
                    :parser="(value: any) => value.replace('%', '')" />
                <MinusCircleOutlined @click="removeHBreakpoint(item)" style="margin-left: 1vw;" />
            </a-form-item>
            <a-form-item name="span" :label="formState.split_h_breakpoints.length === 0 ? '水平分割线' : ' '"
                :colon="formState.split_h_breakpoints.length === 0 ? true : false"
                v-if="formState.op == 'split' && formState.split_type == 'custom'">
                <a-button type="dashed" block @click="addHBreakpoint">
                    <PlusOutlined />
                    添加水平分割线
                </a-button>
            </a-form-item>
            <a-form-item :label="index === 0 ? '垂直分割线' : ' '" :colon="index === 0 ? true : false"
                v-if="formState.op == 'split' && formState.split_type == 'custom'"
                v-for="(item, index) in formState.split_v_breakpoints" :key="index">
                <a-input-number :min="0" :max="100" :formatter="(value: any) => `${value}%`"
                    :parser="(value: any) => value.replace('%', '')" />
                <MinusCircleOutlined @click="removeVBreakpoint(item)" style="margin-left: 1vw;" />
            </a-form-item>
            <a-form-item name="span" :label="formState.split_v_breakpoints.length === 0 ? '垂直分割线' : ' '"
                :colon="formState.split_v_breakpoints.length === 0 ? true : false"
                v-if="formState.op == 'split' && formState.split_type == 'custom'">
                <a-button type="dashed" block @click="addVBreakpoint">
                    <PlusOutlined />
                    添加垂直分割线
                </a-button>
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
                <a-button type="primary" html-type="submit" @click="onSubmit" :loading="confirmLoading">确认</a-button>
                <a-button style="margin-left: 10px" @click="resetFields">重置</a-button>
            </a-form-item>
        </a-form>
    </div>
</template>
<script lang="ts">
import { defineComponent, reactive, watch, ref } from 'vue';
import { message, Modal } from 'ant-design-vue';
import { CheckFileExists, CheckRangeFormat } from '../../../wailsjs/go/main/App';
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
            op: "crop",
            unit: "cm",
            up: 0,
            left: 0,
            down: 0,
            right: 0,
            split_h_breakpoints: [],
            split_v_breakpoints: [],
            split_type: "even",
            split_rows: 1,
            split_cols: 1
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
                validateStatus.input = 'error';
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
                validateStatus.input = 'error';
                validateHelp["input"] = "仅支持pdf格式的文件";
                return Promise.reject();
            }
        };
        const validateRange = async (_rule: Rule, value: string) => {
            validateStatus["page"] = 'validating';
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

        // 分割PDF
        const addHBreakpoint = () => {
            formState.split_h_breakpoints.push(0);
        }
        const removeHBreakpoint = (item: number) => {
            const index = formState.split_h_breakpoints.indexOf(item);
            if (index != -1) {
                formState.split_h_breakpoints.splice(index, 1);
            }
        }
        const addVBreakpoint = () => {
            formState.split_v_breakpoints.push(0);
        }
        const removeVBreakpoint = (item: number) => {
            const index = formState.split_v_breakpoints.indexOf(item);
            if (index != -1) {
                formState.split_v_breakpoints.splice(index, 1);
            }
        }
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
                // await handleOps(OCR, [formState.input, formState.output, formState.page, formState.lang, formState.double_column]);
                confirmLoading.value = false;
            } catch (err) {
                console.log({ err });
                message.error("表单验证失败");
            }
        }
        return {
            formState,
            rules,
            formRef,
            validateStatus,
            validateHelp,
            confirmLoading,
            addHBreakpoint,
            removeHBreakpoint,
            addVBreakpoint,
            removeVBreakpoint,
            resetFields,
            onSubmit
        };
    }
})
</script>