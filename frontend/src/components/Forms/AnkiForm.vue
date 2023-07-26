<template>
    <div>
        <a-form ref="formRef" style="border: 1px solid #dddddd; padding: 10px 0;border-radius: 10px;margin-right: 5vw;"
            :model="store" :label-col="{ span: 3 }" :wrapper-col="{ offset: 1, span: 18 }" :rules="rules" @finish="onFinish"
            @finishFailed="onFinishFailed">
            <a-form-item name="card_type" label="卡片类型">
                <a-radio-group button-style="solid" v-model:value="store.card_type">
                    <a-radio-button value="mask">图片挖空</a-radio-button>
                    <a-radio-button value="qa">问答题</a-radio-button>
                </a-radio-group>
            </a-form-item>
            <a-divider></a-divider>
            <div v-if="store.card_type === 'mask'">
                <a-form-item name="rotate" label="操作类型">
                    <a-radio-group v-model:value="store.op">
                        <a-radio value="annot">根据矩形注释</a-radio>
                        <a-radio value="font">根据字体属性</a-radio>
                    </a-radio-group>
                </a-form-item>
                <div v-if="store.op === 'annot'">
                    <a-form-item label="连接地址">
                        <a-input v-model:value="store.address"></a-input>
                    </a-form-item>
                    <a-form-item label="父牌组">
                        <a-select v-model:value="store.parent_deckname" placeholder="选择父牌组" allow-clear :options="deckNames"
                            :loading="select_loding">
                        </a-select>
                    </a-form-item>
                    <div v-if="!store.is_image">
                        <a-form-item label="创建子牌组">
                            <div>
                                <a-row :gutter="30">
                                    <a-col :span="1">
                                        <a-tooltip>
                                            <template #title>是否根据目录自动创建子牌组</template>
                                            <a-checkbox v-model:checked="store.is_create_sub_deck"></a-checkbox>
                                        </a-tooltip>
                                    </a-col>
                                    <a-col :span="6" v-if="store.is_create_sub_deck">
                                        <a-select v-model:value="store.level">
                                            <a-select-option :value="1">一级标题</a-select-option>
                                            <a-select-option :value="2">二级标题</a-select-option>
                                            <a-select-option :value="3">三级标题</a-select-option>
                                        </a-select>
                                    </a-col>
                                </a-row>
                            </div>
                        </a-form-item>
                    </div>
                    <a-form-item label="图片挖空">
                        <a-tooltip>
                            <template #title>开启后将整页当作图片，无需提供卡片外边框</template>
                            <a-checkbox v-model:checked="store.is_image"></a-checkbox>
                        </a-tooltip>
                    </a-form-item>
                    <a-divider></a-divider>
                    <a-form-item label="制卡模式">
                        <a-checkbox-group v-model:value="store.mode">
                            <a-checkbox value="hide_one_guess_one">
                                <span>遮一猜一</span>
                            </a-checkbox>
                            <a-checkbox value="hide_all_guess_one">
                                <span>遮全猜一</span>
                            </a-checkbox>
                            <a-checkbox value="hide_all_guess_all">
                                <span>遮全猜全</span>
                            </a-checkbox>
                        </a-checkbox-group>
                    </a-form-item>
                    <a-form-item label="遮罩类型">
                        <a-checkbox-group v-model:value="store.mask_types">
                            <!-- <a-checkbox value="rect" disabled>
                                <span>矩形注释</span>
                            </a-checkbox> -->
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
                        </a-checkbox-group>
                    </a-form-item>
                    <a-form-item label="遮罩颜色">
                        <div>
                            <a-row :gutter="3">
                                <a-col>
                                    <a-space>
                                        <a-tooltip>
                                            <template #title>问题mask颜色</template>
                                            <a-input v-model:value="store.q_mask_color" placeholder="问题遮罩颜色"
                                                :defaultValue="store.q_mask_color" allow-clear>
                                                <template #addonBefore>
                                                    Q
                                                </template>
                                                <template #prefix>
                                                    <font-colors-outlined />
                                                </template>
                                            </a-input>
                                        </a-tooltip>
                                        <color-picker v-model:pureColor="pureColorQMask"
                                            v-model:gradientColor="gradientColor" shape="square" use-type="pure"
                                            format="hex6" @pureColorChange="handleColorChangeQMask" />
                                    </a-space>
                                </a-col>
                                <a-col>
                                    <a-space>
                                        <a-tooltip>
                                            <template #title>答案mask颜色</template>
                                            <a-input v-model:value="store.a_mask_color" placeholder="答案遮罩颜色"
                                                :defaultValue="store.a_mask_color" allow-clear>
                                                <template #addonBefore>
                                                    A
                                                </template>
                                                <template #prefix>
                                                    <font-colors-outlined />
                                                </template>
                                            </a-input>
                                        </a-tooltip>
                                        <color-picker v-model:pureColor="pureColorAMask"
                                            v-model:gradientColor="gradientColor" shape="square" use-type="pure"
                                            format="hex6" @pureColorChange="handleColorChangeAMask" />
                                    </a-space>
                                </a-col>
                            </a-row>
                        </div>
                    </a-form-item>
                    <a-form-item label="卡片标签">
                        <a-select v-model:value="store.tags" mode="tags" style="width: 100%" :options="tag_names"
                            placeholder="输入卡片标签,可留空"></a-select>
                    </a-form-item>
                    <a-form-item label="分辨率(dpi)">
                        <a-input-number v-model:value="store.dpi" :min="100" :max="1200" :step="100"></a-input-number>
                    </a-form-item>
                </div>
                <div v-if="store.op === 'font'">
                    <a-form-item label="匹配条件">
                        <a-checkbox-group v-model:value="store.matches">
                            <a-checkbox value="same_font">
                                <span>同字体</span>
                            </a-checkbox>
                            <a-checkbox value="same_size">
                                <span>同大小</span>
                            </a-checkbox>
                            <a-checkbox value="same_color">
                                <span>同颜色</span>
                            </a-checkbox>
                            <a-checkbox value="same_flags">
                                <span>同外形(粗体、斜体、下划线等)</span>
                            </a-checkbox>
                        </a-checkbox-group>
                    </a-form-item>
                    <!-- <a-form-item label="卡片大小">
                    <a-select v-model:value="store.card_size">
                        <a-select-option value="1">一空一卡</a-select-option>
                        <a-select-option value="2">一段一卡</a-select-option>
                        <a-select-option value="3">一页一卡</a-select-option>
                    </a-select>
                </a-form-item> -->
                </div>
            </div>
            <div v-if="store.card_type === 'qa'">
                <a-form-item label="连接地址">
                    <a-input v-model:value="store.address"></a-input>
                </a-form-item>
                <a-form-item label="父牌组">
                    <a-select v-model:value="store.parent_deckname" placeholder="选择父牌组" allow-clear :options="deckNames"
                        :loading="select_loding">
                    </a-select>
                </a-form-item>
                <a-form-item label="模板">
                    <a-select v-model:value="store.modelname" placeholder="选择模板" allow-clear :options="modelNames"
                        :loading="select_loding" @change="handModelChange">
                    </a-select>
                </a-form-item>
                <div>
                    <a-form-item label="创建子牌组">
                        <div>
                            <a-row :gutter="30">
                                <a-col :span="1">
                                    <a-tooltip>
                                        <template #title>是否根据目录自动创建子牌组</template>
                                        <a-checkbox v-model:checked="store.is_create_sub_deck"></a-checkbox>
                                    </a-tooltip>
                                </a-col>
                                <a-col :span="6" v-if="store.is_create_sub_deck">
                                    <a-select v-model:value="store.level">
                                        <a-select-option :value="1">一级标题</a-select-option>
                                        <a-select-option :value="2">二级标题</a-select-option>
                                        <a-select-option :value="3">三级标题</a-select-option>
                                    </a-select>
                                </a-col>
                            </a-row>
                        </div>
                    </a-form-item>
                </div>
                <a-form-item label="字段映射">
                    <div>
                        <a-row :gutter="8">
                            <a-col :span="12">
                                <a-select v-model:value="store.front_field" placeholder="选择正面字段" label-in-value allow-clear
                                    :options="field_names" :loading="select_loding">
                                </a-select>
                            </a-col>
                            <a-col :span="12">
                                <a-select v-model:value="store.back_field" placeholder="选择背面字段" label-in-value allow-clear
                                    :options="field_names" :loading="select_loding">
                                </a-select>
                            </a-col>
                        </a-row>
                    </div>
                </a-form-item>
                <a-form-item label="卡片标签">
                    <a-select v-model:value="store.tags" mode="tags" style="width: 100%" :options="tag_names"
                        placeholder="输入卡片标签,可留空"></a-select>
                </a-form-item>
                <a-form-item label="分辨率(dpi)">
                    <a-input-number v-model:value="store.dpi" :min="100" :max="1200" :step="100"></a-input-number>
                </a-form-item>
            </div>
            <a-divider></a-divider>

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
            <div v-if="store.op !== 'annot'">
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
            <a-form-item :wrapperCol="{ offset: 4 }" style="margin-bottom: 10px;">
                <a-button type="primary" html-type="submit" :loading="confirmLoading">确认</a-button>
                <a-button style="margin-left: 10px" @click="resetFields">重置</a-button>
            </a-form-item>
        </a-form>
    </div>
</template>
<script lang="ts">
import { defineComponent, reactive, onMounted, ref, watch, toRaw } from 'vue';
import { message, Modal } from 'ant-design-vue';
import {
    SelectFile,
    SaveFile,
    CheckFileExists,
    CheckRangeFormat,
    GetDeckNames,
    GetModelNames,
    GetModelFieldNames,
    GetTags,
    CreateCardByRectAnnots,
    CreateCardByFontStyle,
    CreateQACard,
} from '../../../wailsjs/go/main/App';
import type { FormInstance } from 'ant-design-vue';
import { EllipsisOutlined, FontColorsOutlined } from '@ant-design/icons-vue';
import type { Rule } from 'ant-design-vue/es/form';
import { handleOps } from "../data";
import { useAnkiState } from '../../store/anki';
import type { SelectProps } from 'ant-design-vue';
import { ColorPicker } from "vue3-colorpicker";
import "vue3-colorpicker/style.css";
// @ts-ignore
import { ColorInputWithoutInstance } from "tinycolor2";

export default defineComponent({
    components: {
        EllipsisOutlined,
        FontColorsOutlined,
        ColorPicker
    },
    setup() {
        const formRef = ref<FormInstance>();
        const store = useAnkiState();
        const deckNames = ref<SelectProps['options']>([
        ]);
        const modelNames = ref<SelectProps['options']>([
        ]);
        const field_names = ref<SelectProps['options']>([
        ]);
        const tag_names = ref<SelectProps['options']>([
        ]);
        const select_loding = ref(false);
        const load_names = async () => {
            select_loding.value = true;
            await GetDeckNames(store.address).then((res: string[]) => {
                console.log({ res });
                deckNames.value = res.map((name) => {
                    return {
                        label: name,
                        value: name,
                    }
                });
                store.parent_deckname = undefined;
            }).catch((err: any) => {
                console.log({ err });
                message.error("获取牌组名称失败!");
            });
            await GetModelNames(store.address).then((res: string[]) => {
                console.log({ res });
                modelNames.value = res.map((name) => {
                    return {
                        label: name,
                        value: name,
                    }
                });
                store.modelname = undefined;
            }).catch((err: any) => {
                console.log({ err });
                message.error("获取模板名称失败!");
            });
            // @ts-ignore
            // await GetModelFieldNames(store.address, store.modelname).then((res: string[]) => {
            //     console.log({ res });
            //     field_names.value = res.map((name) => {
            //         return {
            //             label: name,
            //             value: name,
            //         }
            //     });
            // }).catch((err: any) => {
            //     console.log({ err });
            //     message.error("获取模板字段名称失败!");
            // });
            await GetTags(store.address).then((res: string[]) => {
                console.log({ res });
                tag_names.value = res.map((name) => {
                    return {
                        label: name,
                        value: name,
                    }
                });
            }).catch((err: any) => {
                console.log({ err });
                message.error("获取标签名称失败!");
            });
            select_loding.value = false;
            store.front_field = undefined;
            store.back_field = undefined;
        }
        onMounted(async () => {
            await load_names();
        });

        const handModelChange = async () => {
            // @ts-ignore
            await GetModelFieldNames(store.address, store.modelname).then((res: string[]) => {
                console.log({ res });
                store.front_field = undefined;
                store.back_field = undefined;
                field_names.value = res.map((name) => {
                    return {
                        label: name,
                        value: name,
                    }
                });
            }).catch((err: any) => {
                console.log({ err });
                message.error("获取模板字段名称失败!");
            });
        }
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
            if(store.parent_deckname === undefined){
                message.error("请选择父牌组");
                return;
            }
            if(store.card_type === "qa"){
                if(store.modelname === undefined){
                    message.error("请选择模板");
                    return;
                }
            }
            switch (store.card_type) {
                case "mask": {
                    confirmLoading.value = true;
                    switch (store.op) {
                        case "annot": {
                            await handleOps(CreateCardByRectAnnots, [
                                store.input,
                                store.output,
                                store.address,
                                store.parent_deckname,
                                store.mode,
                                store.is_create_sub_deck,
                                store.level,
                                store.q_mask_color,
                                store.a_mask_color,
                                store.dpi,
                                store.tags,
                                store.is_image,
                                store.mask_types,
                                store.page
                            ])
                            break;
                        }
                        case "font": {
                            await handleOps(CreateCardByFontStyle, [
                                store.input,
                                store.output,
                                store.matches,
                                // store.card_size,
                                store.page
                            ]);
                            break;
                        }
                    }
                    break;
                }
                case "qa": {
                    if (store.front_field === undefined || store.back_field === undefined) {
                        message.error("请选择字段映射");
                        return;
                    }
                    // @ts-ignore
                    if (toRaw(store.front_field)['value'] === toRaw(store.back_field)['value']) {
                        message.error("正面字段和背面字段不能相同");
                        return;
                    }
                    confirmLoading.value = true;
                    // @ts-ignore
                    let field_mappings = `{"question": "${toRaw(store.front_field)['value']}", "answer": "${toRaw(store.back_field)['value']}"}`
                    console.log({ field_mappings });
                    await handleOps(CreateQACard, [
                        store.input,
                        store.output,
                        store.address,
                        store.parent_deckname,
                        store.modelname,
                        field_mappings,
                        store.is_create_sub_deck,
                        store.level,
                        store.dpi,
                        store.tags,
                        store.page
                    ]);
                    break;
                }
            }
            confirmLoading.value = false;
            await load_names();
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

        const pureColorQMask = ref<ColorInputWithoutInstance>(store.q_mask_color);
        const pureColorAMask = ref<ColorInputWithoutInstance>(store.a_mask_color);
        const gradientColor = ref("linear-gradient(0deg, rgba(0, 0, 0, 1) 0%, rgba(0, 0, 0, 1) 100%)");
        const handleColorChangeQMask = (color: ColorInputWithoutInstance) => {
            console.log({ color });
            store.q_mask_color = color;
        };
        const handleColorChangeAMask = (color: ColorInputWithoutInstance) => {
            console.log({ color });
            store.a_mask_color = color;
        };
        watch(() => store.q_mask_color, (newVal, oldVal) => {
            console.log({ newVal, oldVal });
            pureColorQMask.value = newVal;
        })
        watch(() => store.a_mask_color, (newVal, oldVal) => {
            console.log({ newVal, oldVal });
            pureColorAMask.value = newVal;
        })
        return {
            confirmLoading,
            deckNames,
            modelNames,
            field_names,
            tag_names,
            formRef,
            gradientColor,
            handleColorChangeAMask,
            handleColorChangeQMask,
            handModelChange,
            onFinish,
            onFinishFailed,
            pureColorAMask,
            pureColorQMask,
            resetFields,
            rules,
            saveFile,
            select_loding,
            selectFile,
            store,
            validateHelp,
            validateStatus,
        };
    }
})
</script>