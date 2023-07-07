<template>
    <div>
        <a-form ref="formRef" style="border: 1px solid #dddddd; padding: 10px 0;border-radius: 10px;margin-right: 5vw;"
            :model="formState" :label-col="{ span: 3 }" :wrapper-col="{ offset: 1, span: 18 }" :rules="rules"
            @finish="onFinish" @finishFailed="onFinishFailed">
            <a-form-item name="encrypt_op" label="操作" style="margin-bottom: 1.8vh;">
                <a-radio-group button-style="solid" v-model:value="formState.op">
                    <a-radio-button value="add">添加页码</a-radio-button>
                    <a-radio-button value="remove">删除页码</a-radio-button>
                </a-radio-group>
            </a-form-item>
            <a-form-item name="pos" label="页码位置">
                <a-radio-group v-model:value="formState.pos">
                    <a-radio value="header">页眉</a-radio>
                    <a-radio value="footer">页脚</a-radio>
                </a-radio-group>
            </a-form-item>
            <div v-if="formState.op === 'add'">
                <a-form-item name="align" label="对齐方式">
                    <a-radio-group v-model:value="formState.align">
                        <a-radio value="left">左对齐</a-radio>
                        <a-radio value="center">居中</a-radio>
                        <a-radio value="right">右对齐</a-radio>
                    </a-radio-group>
                </a-form-item>
                <a-form-item label="起始页码">
                    <a-input-number v-model:value="formState.number_start"></a-input-number>
                </a-form-item>
                <a-form-item label="页码样式">
                    <a-select v-model:value="formState.number_style" style="width: 200px">
                        <a-select-option value="0">1,2,3...</a-select-option>
                        <a-select-option value="1">1/X</a-select-option>
                        <a-select-option value="2">第1页</a-select-option>
                        <a-select-option value="3">第1/X页</a-select-option>
                        <a-select-option value="4">第1页，共X页</a-select-option>
                        <a-select-option value="5">-1-,-2-,-3-...</a-select-option>
                        <a-select-option value="6">第一页</a-select-option>
                        <a-select-option value="7">第一页，共X页</a-select-option>
                        <a-select-option value="8">I,II,III...</a-select-option>
                        <a-select-option value="9">i,ii,iii...</a-select-option>
                        <a-select-option value="10">A,B,C...</a-select-option>
                        <a-select-option value="11">a,b,c...</a-select-option>
                    </a-select>
                </a-form-item>
                <a-form-item label="自定义页码样式">
                    <a-checkbox v-model:checked="formState.is_custom_style"></a-checkbox>
                </a-form-item>
                <a-form-item label="页码格式" v-if="formState.is_custom_style">
                    <a-input v-model:value="formState.custom_style" placeholder="自定义页码格式, %p表示当前页码，%P表示总页码，e.g. '第%p/%P页'"
                        allow-clear :disabled="!formState.is_custom_style" />
                </a-form-item>
                <a-form-item name="watermark_font_size" label="字体属性" hasFeedback>
                    <a-space size="large">
                        <a-select v-model:value="formState.font_family" style="width: 200px">
                            <a-select-option value="msyh.ttc">微软雅黑</a-select-option>
                            <a-select-option value="simsun.ttc">宋体</a-select-option>
                            <a-select-option value="simhei.ttf">黑体</a-select-option>
                            <a-select-option value="simkai.ttf">楷体</a-select-option>
                            <a-select-option value="simfang.ttf">仿宋</a-select-option>
                            <a-select-option value="SIMYOU.TTF">幼圆</a-select-option>
                            <a-select-option value="STHUPO.TTF">华文琥珀</a-select-option>
                            <a-select-option value="FZSTK.TTF">方正舒体</a-select-option>
                            <a-select-option value="STZHONGS.TTF">华文中宋</a-select-option>
                            <a-select-option value="arial.ttf">Arial</a-select-option>
                            <a-select-option value="times.ttf">TimesNewRoman</a-select-option>
                            <a-select-option value="calibri.ttf">Calibri</a-select-option>
                            <a-select-option value="consola.ttf">Consola</a-select-option>
                        </a-select>
                        <a-tooltip>
                            <template #title>字号</template>
                            <a-input-number v-model:value="formState.font_size" :min="1">
                                <template #prefix>
                                    <font-size-outlined />
                                </template>
                            </a-input-number>
                        </a-tooltip>
                        <a-tooltip>
                            <template #title>字体颜色</template>
                            <a-input v-model:value="formState.font_color" placeholder="16进制字体颜色"
                                :defaultValue="formState.font_color" allow-clear>
                                <template #prefix>
                                    <font-colors-outlined />
                                </template>
                            </a-input>
                        </a-tooltip>
                        <a-tooltip>
                            <template #title>不透明度</template>
                            <a-input-number v-model:value="formState.opacity" :min="0" :max="1" :step="0.01">
                                <template #addonBefore>
                                    不透明度
                                </template>
                            </a-input-number>
                        </a-tooltip>
                    </a-space>
                </a-form-item>
            </div>
            <a-form-item label="页边距单位">
                <a-radio-group v-model:value="formState.unit">
                    <a-radio value="pt">像素</a-radio>
                    <a-radio value="cm">厘米</a-radio>
                    <a-radio value="mm">毫米</a-radio>
                    <a-radio value="in">英寸</a-radio>
                </a-radio-group>
            </a-form-item>
            <a-form-item name="crop.type" label="页边距">
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
import { CheckFileExists, CheckRangeFormat, AddPDFPageNumber, RemovePDFPageNumber } from '../../../wailsjs/go/main/App';
import type { FormInstance } from 'ant-design-vue';
import type { Rule } from 'ant-design-vue/es/form';
import { FontSizeOutlined, FontColorsOutlined } from '@ant-design/icons-vue';
import type { PageNumberState } from "../data";
import { handleOps } from "../data";
export default defineComponent({
    components: {
        FontSizeOutlined,
        FontColorsOutlined
    },
    setup() {
        const formRef = ref<FormInstance>();
        const formState = reactive<PageNumberState>({
            input: "",
            output: "",
            page: "",
            op: 'add',
            pos: 'footer',
            number_style: '1',
            number_start: 1,
            custom_style: '',
            is_custom_style: false,
            align: 'center',
            font_family: 'simsun.ttc',
            font_size: 14,
            font_color: '#000000',
            up: 1.27,
            down: 1.27,
            left: 2.54,
            right: 2.54,
            opacity: 1,
            unit: 'cm'
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
            formRef.value?.resetFields();
        }
        // 提交表单
        const confirmLoading = ref<boolean>(false);
        async function submit() {
            confirmLoading.value = true;
            switch (formState.op) {
                case 'add': {
                    let format = formState.number_style;
                    if (formState.is_custom_style) {
                        format = formState.custom_style;
                    }
                    await handleOps(AddPDFPageNumber, [
                        formState.input,
                        formState.output,
                        formState.pos,
                        formState.number_start,
                        format,
                        [formState.up, formState.down, formState.left, formState.right],
                        formState.unit,
                        formState.align,
                        formState.font_family,
                        formState.font_size,
                        formState.font_color,
                        formState.opacity,
                        formState.page,
                    ])
                    break;
                }
                case 'remove': {
                    await handleOps(RemovePDFPageNumber, [
                        formState.input,
                        formState.output,
                        [formState.up, formState.down, formState.left, formState.right],
                        formState.pos,
                        formState.unit,
                        formState.page,
                    ])
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
        return { formState, rules, formRef, validateStatus, validateHelp, confirmLoading, resetFields, onFinish, onFinishFailed };
    }
})
</script>