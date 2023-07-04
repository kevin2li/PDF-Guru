<template>
    <div>
        <a-form ref="formRef" style="border: 1px solid #dddddd; padding: 10px 0;border-radius: 10px;margin-right: 5vw;"
            :model="formState" :label-col="{ span: 3 }" :wrapper-col="{ offset: 1, span: 18 }" :rules="rules"
            @finish="onFinish" @finishFailed="onFinishFailed">
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
                <a-form-item name="page" hasFeedback :validateStatus="validateStatus.page" :help="validateHelp.page"
                    label="页码范围">
                    <a-input v-model:value="formState.page" placeholder="应用的页码范围(留空表示全部), e.g. 1-10" allow-clear />
                </a-form-item>
            </div>
            <div v-if="formState.op === 'remove'">
                <a-form-item name="remove_method" label="去水印方法">
                    <a-radio-group v-model:value="formState.remove_method">
                        <a-radio value="type">自动查找水印去除</a-radio>
                        <a-radio value="index">人工识别水印索引</a-radio>
                    </a-radio-group>
                </a-form-item>
                <div v-if="formState.remove_method === 'type'">
                    <a-form-item name="page" hasFeedback :validateStatus="validateStatus.page" :help="validateHelp.page"
                        label="页码范围">
                        <a-input v-model:value="formState.page" placeholder="应用的页码范围(留空表示全部), e.g. 1-10" allow-clear />
                    </a-form-item>
                </div>
                <div v-if="formState.remove_method === 'index'">
                    <a-form-item name="step" label="步骤">
                        <a-radio-group v-model:value="formState.step">
                            <a-radio style="display: flex;height:30px;lineHeight:30px;" value="1">步骤一：识别水印索引</a-radio>
                            <a-radio style="display: flex;height:30px;lineHeight:30px;" value="2">步骤二：删除水印</a-radio>
                        </a-radio-group>
                    </a-form-item>
                    <a-form-item name="page" label="含水印页码" v-if="formState.step === '1'">
                        <a-input v-model:value="formState.wm_index" placeholder="包含水印的页码，1页即可"></a-input>
                    </a-form-item>
                    <a-form-item name="page" label="水印索引" v-if="formState.step === '2'">
                        <a-input v-model:value="formState.wm_index" placeholder="多个数字用英文逗号隔开, e.g. 5"></a-input>
                    </a-form-item>
                    <a-form-item name="page" hasFeedback :validateStatus="validateStatus.page" :help="validateHelp.page"
                        label="页码范围" v-if="formState.step === '2'">
                        <a-input v-model:value="formState.page" placeholder="应用的页码范围(留空表示全部), e.g. 1-10" allow-clear />
                    </a-form-item>
                </div>
            </div>
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
import { CheckFileExists, CheckRangeFormat, WatermarkPDF, RemoveWatermarkByIndex, RemoveWatermarkByType, DetectWatermarkByIndex } from '../../../wailsjs/go/main/App';
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
            remove_method: "type",
            step: "1",
            wm_index: ""
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
                case "add": {
                    await handleOps(WatermarkPDF, [formState.input, formState.output, formState.text, formState.font_family, formState.font_size, formState.font_color, formState.rotate, formState.space, formState.font_opacity, formState.quaility]);
                    break;
                }
                case "remove": {
                    switch (formState.remove_method) {
                        case "type": {
                            await handleOps(RemoveWatermarkByType, [formState.input, formState.output, formState.page]);
                            break;
                        }
                        case "index": {
                            switch (formState.step) {
                                case "1": {
                                    let wm_index = formState.wm_index.split(",").map((item) => parseInt(item.trim()));
                                    await handleOps(DetectWatermarkByIndex, [formState.input, formState.output, wm_index[0]]);
                                    break;
                                }
                                case "2": {
                                    let wm_index = formState.wm_index.split(",").map((item) => parseInt(item.trim()) - 1);
                                    await handleOps(RemoveWatermarkByIndex, [formState.input, formState.output, wm_index, formState.page]);
                                    break;
                                }
                            }
                            break;
                        }
                    }
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