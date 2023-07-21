<template>
    <div class="signature-pad">
        <a-form ref="formRef" style="border: 1px solid #dddddd; padding: 10px 0;border-radius: 10px;margin-right: 5vw;"
            :model="store" :label-col="{ span: 3 }" :rules="rules" :wrapper-col="{ offset: 1, span: 18 }" @finish="onFinish"
            @finishFailed="onFinishFailed">
            <a-form-item label="来源">
                <a-radio-group v-model:value="store.op">
                    <a-radio value="image">图片</a-radio>
                    <!-- <a-radio value="input">输入</a-radio> -->
                    <a-radio value="hand">手写</a-radio>
                </a-radio-group>
            </a-form-item>
            <div v-if="store.op === 'image'">
                <a-form-item name="input" label="输入" :validateStatus="validateStatus.input" :help="validateHelp.input">
                    <div>
                        <a-row>
                            <a-col :span="22">
                                <a-input v-model:value="store.input" placeholder="输入文件路径" allow-clear />
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
            </div>
            <div v-if="store.op === 'input'">
                <a-form-item label="内容">
                    <a-input v-model:value="store.text" placeholder="输入签名内容"></a-input>
                </a-form-item>
                <a-form-item label="字体">
                    <a-select v-model:value="store.font_family" style="width: 200px" :options="font_options">
                    </a-select>
                </a-form-item>
            </div>
            <div v-if="store.op === 'hand'">
                <a-form-item label="粗细">
                    <a-space>
                        <a-input-number :min="1" v-model:value="store.font_size" />
                        <div style="width: 200px;">
                            <a-slider v-model:value="store.font_size" :min="1" :max="50"></a-slider>
                        </div>
                    </a-space>
                </a-form-item>
                <a-form-item label="颜色">
                    <!-- <a-color-picker v-model:value="store.color" /> -->
                    <a-space>
                        <a-input v-model:value="store.font_color" style="width: 100px;"></a-input>
                        <color-picker v-model:pureColor="pureColor" v-model:gradientColor="gradientColor" shape="square"
                            use-type="pure" format="hex6" @pureColorChange="handleColorChange" />
                    </a-space>
                </a-form-item>
                <a-form-item label="模拟压感">
                    <a-checkbox v-model:checked="store.is_pressure"></a-checkbox>
                </a-form-item>
                <a-form-item label="画板">
                    <div style="border: 1px solid #ddd;cursor: crosshair;">
                        <VPerfectSignature :stroke-options="stroke_options" :pen-color="store.font_color"
                            :simulatePressure="store.is_pressure" ref="signaturePad" @on-begin="handleBegin"
                            @on-end="handleEnd" />
                    </div>
                </a-form-item>
            </div>
            <div v-if="store.op !== 'hand'">
                <a-form-item :wrapperCol="{ offset: 4 }" style="margin-bottom: 10px;">
                    <a-button type="primary" html-type="submit" :loading="confirmLoading">确认</a-button>
                    <a-button style="margin-left: 10px" @click="resetFields">重置</a-button>
                </a-form-item>
            </div>
            <div v-else style="margin-top: 1vh;">
                <a-form-item :wrapperCol="{ offset: 4 }" style="margin-bottom: 10px;">
                    <a-space>
                        <a-button @click="clear">
                            <ClearOutlined /> 清除
                        </a-button>
                        <a-button @click="handleUndo" :disabled="!signData.canUndo">
                            <UndoOutlined /> 撤销
                        </a-button>
                        <a-button @click="handleRedo" :disabled="!signData.canRedo">
                            <RedoOutlined /> 恢复
                        </a-button>
                        <a-button type="primary" @click="toDataURL">
                            <SaveOutlined /> 保存
                        </a-button>
                    </a-space>
                </a-form-item>
            </div>
        </a-form>
    </div>
</template>
<script lang="ts">
import { defineComponent, reactive, ref, onMounted, watch, unref } from 'vue';
import { VPerfectSignature } from 'v-perfect-signature';
import { useSignState } from '../../store/sign';
import { message, Modal } from 'ant-design-vue';
import type { FormInstance } from 'ant-design-vue';
import type { Rule } from 'ant-design-vue/es/form';
import {
    EllipsisOutlined,
    UndoOutlined,
    RedoOutlined,
    SaveOutlined,
    ClearOutlined,
} from '@ant-design/icons-vue';
import { handleOps, windows_fonts_options, mac_fonts_options } from "../data";
import {
    SignImage,
} from '../../../wailsjs/go/main/App';
import type { SelectProps } from 'ant-design-vue';
import { ColorPicker } from "vue3-colorpicker";
import "vue3-colorpicker/style.css";
// @ts-ignore
import { ColorInputWithoutInstance } from "tinycolor2";

import {
    CheckOS,
    SelectFile,
    SaveFile,
    CheckFileExists
} from '../../../wailsjs/go/main/App';

export default defineComponent({
    components: {
        VPerfectSignature,
        ColorPicker,
        EllipsisOutlined,
        UndoOutlined,
        RedoOutlined,
        SaveOutlined,
        ClearOutlined,
    },
    setup() {
        const signaturePad = ref(null);
        const store = useSignState();
        const confirmLoading = ref<boolean>(false);
        const formRef = ref<FormInstance>();
        const font_options = ref<SelectProps['options']>([]);
        const setFontOptions = async () => {
            await CheckOS().then((res: any) => {
                if (res === "windows") {
                    font_options.value = windows_fonts_options;
                    store.font_family = 'msyh.ttc';
                } else if (res === "darwin") {
                    font_options.value = mac_fonts_options;
                    store.font_family = 'STHeiti Light.ttc';
                }
            }).catch((err: any) => {
                console.log({ err });
            })
        }
        onMounted(async () => {
            await setFontOptions();
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
        };
        const rules: Record<string, Rule[]> = {
            input: [{ required: true, validator: validateFileExists, trigger: 'change' }],
        };
        const stroke_options = reactive({
            size: store.font_size,
            thinning: store.thinning,
            smoothing: store.smoothing,
            streamline: store.streamline,
            simulatePressure: store.is_pressure,
        });

        watch([() => store.font_size, () => store.font_color, () => store.is_pressure], ([newSize, newColor, newPressure], [oldSize, oldColor, oldPressure]) => {
            stroke_options.size = newSize;
            // @ts-ignore
            stroke_options.simulatePressure = newPressure;
            // @ts-ignore
            signaturePad.value.clear();
            // @ts-ignore
            signaturePad.value.fromData(signData.points.slice(0, signData.pointer + 1));
        });
        const signData = reactive<{
            points: any[];
            pointer: number;
            canUndo: boolean;
            canRedo: boolean;
        }>({
            points: [],
            pointer: -1,
            canUndo: false,
            canRedo: false,
        })
        function toDataURL() {
            // @ts-ignore
            if (signaturePad.value.isEmpty()) {
                message.error("请先签名");
                return;
            }
            // @ts-ignore
            const dataURL = signaturePad.value.toDataURL();
            console.log(dataURL);
            // download image
            const link = document.createElement('a');
            link.download = `signature-${Date.now()}.png`;
            link.href = dataURL;
            link.click();
        }
        function clear() {
            // @ts-ignore
            signaturePad.value.clear();
            signData.points = [];
            signData.pointer = -1;
            signData.canUndo = false;
            signData.canRedo = false;
        }
        const handleBegin = () => {
        }
        const handleEnd = () => {
            // @ts-ignore
            const cur_points = signaturePad.value.toData();
            signData.points = cur_points;
            signData.pointer = cur_points.length - 1;
            signData.canUndo = true;
            console.log({ signData })
        }
        const handleUndo = () => {
            // @ts-ignore
            signaturePad.value.clear();

            // @ts-ignore
            signaturePad.value.fromData(signData.points.slice(0, signData.pointer));
            signData.pointer -= 1;
            signData.canUndo = signData.pointer >= 0;
            signData.canRedo = true;
        }
        const handleRedo = () => {
            // @ts-ignore
            signaturePad.value.clear();
            signData.pointer += 1;
            // @ts-ignore
            signaturePad.value.fromData(signData.points.slice(0, signData.pointer + 1));
            signData.canRedo = signData.pointer < signData.points.length - 1;
            signData.canUndo = true;
        }
        async function submit() {
            confirmLoading.value = true;
            switch (store.op) {
                case "image":
                    await handleOps(SignImage, [store.input, store.output]);
                    break;
            }
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
        const resetFields = () => {
            formRef.value?.clearValidate();
            store.resetState();
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
        const pureColor = ref<ColorInputWithoutInstance>(store.font_color);
        const gradientColor = ref("linear-gradient(0deg, rgba(0, 0, 0, 1) 0%, rgba(0, 0, 0, 1) 100%)");
        const handleColorChange = (color: ColorInputWithoutInstance) => {
            console.log({ color });
            store.font_color = color;
        }
        return {
            confirmLoading,
            signaturePad,
            store,
            formRef,
            stroke_options,
            toDataURL,
            clear,
            onFinish,
            onFinishFailed,
            resetFields,
            font_options,
            selectFile,
            saveFile,
            rules,
            validateStatus,
            validateHelp,
            pureColor,
            gradientColor,
            handleColorChange,
            handleBegin,
            handleEnd,
            handleUndo,
            handleRedo,
            signData,
        };
    }
});
</script>
