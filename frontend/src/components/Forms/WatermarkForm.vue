<template>
    <div>
        <a-form ref="formRef" style="border: 1px solid #dddddd; padding: 10px 0;border-radius: 10px;margin-right: 5vw;"
            :model="formState" :label-col="{ span: 3 }" :wrapper-col="{ offset: 1, span: 18 }" :rules="rules">
            <a-form-item name="watermark_op" label="操作">
                <a-radio-group button-style="solid" v-model:value="formState.op">
                    <a-radio-button value="add">添加水印</a-radio-button>
                    <a-radio-button value="remove">去除水印</a-radio-button>
                </a-radio-group>
            </a-form-item>
            <div v-if="formState.op === 'add'">
                <a-form-item name="watermark_type" label="水印类型">
                    <a-radio-group v-model:value="formState.type">
                        <a-radio value="text">文本</a-radio>
                        <a-radio value="image" disabled>图片</a-radio>
                    </a-radio-group>
                </a-form-item>
                <a-form-item name="watermark_text" label="水印文本">
                    <a-input v-model:value="formState.text" placeholder="e.g. 这是水印" allow-clear />
                </a-form-item>
                <a-form-item name="watermark_font_size" label="字体属性">
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
                            <a-input v-model:value="formState.font_color" placeholder="字体颜色"
                                :defaultValue="formState.font_color" allow-clear>
                                <template #prefix>
                                    <font-colors-outlined />
                                </template>
                            </a-input>
                        </a-tooltip>
                    </a-space>
                </a-form-item>
                <a-form-item name="watermark_font_opacity" label="水印属性">
                    <a-space size="large">
                        <a-input-number v-model:value="formState.font_opacity" :min="0" :max="1" :step="0.01">
                            <template #addonBefore>
                                不透明度
                            </template>
                        </a-input-number>
                        <a-input-number v-model:value="formState.rotate" :min="0" :max="360">
                            <template #addonBefore>
                                旋转角度
                            </template>
                        </a-input-number>
                        <a-input-number v-model:value="formState.space" :min="0" :max="360">
                            <template #addonBefore>
                                文字间距
                            </template>
                        </a-input-number>
                        <a-input-number v-model:value="formState.quaility" :min="0" :max="360">
                            <template #addonBefore>
                                图片质量
                            </template>
                        </a-input-number>
                    </a-space>
                </a-form-item>
            </div>
            <a-form-item name="page" hasFeedback :validateStatus="validateStatus.page" label="页码范围">
                <a-input v-model:value="formState.page" placeholder="应用的页码范围(留空表示全部), e.g. 1-10" allow-clear />
            </a-form-item>
            <a-form-item name="input" label="输入" hasFeedback :validateStatus="validateStatus.input">
                <a-input v-model:value="formState.input" placeholder="输入文件路径" allow-clear />
            </a-form-item>
            <a-form-item name="output" label="输出">
                <a-input v-model:value="formState.output" placeholder="输出目录" allow-clear />
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
import { CheckFileExists, CheckRangeFormat, WatermarkPDF } from '../../../wailsjs/go/main/App';
import type { FormInstance } from 'ant-design-vue';
import type { Rule } from 'ant-design-vue/es/form';
import type { WatermarkState } from "../data";
import { handleOps } from "../data";
export default defineComponent({
    components: {
    },
    setup() {
        const formRef = ref<FormInstance>();
        const formState = reactive<WatermarkState>({
            input: "",
            output: "",
            page: "",
            op: "add",
            type: "text",
            text: "",
            font_family: "msyh.ttc",
            font_size: 14,
            font_color: "#808080",
            font_opacity: 0.15,
            quaility: 80,
            rotate: 30,
            space: 75,
        });

        const validateStatus = reactive({
            input: "",
            page: "",
        });

        const validateFileExists = async (_rule: Rule, value: string) => {
            validateStatus["input"] = 'validating';
            if (value === '') {
                validateStatus.input = 'error';
                return Promise.reject('请填写路径');
            }
            await CheckFileExists(value).then((res: any) => {
                console.log({ res });
                if (res) {
                    validateStatus["input"] = 'error';
                    return Promise.reject(res);
                }
                validateStatus["input"] = 'success';
                return Promise.resolve();
            }).catch((err: any) => {
                console.log({ err });
                validateStatus["input"] = 'error';
                return Promise.reject("文件不存在");
            });
        };
        const validateRange = async (_rule: Rule, value: string) => {
            validateStatus["page"] = 'validating';
            await CheckRangeFormat(value).then((res: any) => {
                console.log({ res });
                if (res) {
                    validateStatus["page"] = 'error';
                    return Promise.reject("页码格式错误");
                }
                validateStatus["page"] = 'success';
                return Promise.resolve();
            }).catch((err: any) => {
                console.log({ err });
                validateStatus["page"] = 'error';
                return Promise.reject("页码格式错误");
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
        const onSubmit = async () => {
            try {
                await formRef.value?.validate();
                confirmLoading.value = true;
                await handleOps(WatermarkPDF, [formState.input, formState.output, formState.text, formState.font_family, formState.font_size, formState.font_color, formState.rotate, formState.space, formState.font_opacity, formState.quaility]);
                confirmLoading.value = false;
            } catch (err) {
                console.log({ err });
                message.error("表单验证失败");
            }
        }
        return { formState, rules, formRef, validateStatus, confirmLoading, resetFields, onSubmit };
    }
})
</script>