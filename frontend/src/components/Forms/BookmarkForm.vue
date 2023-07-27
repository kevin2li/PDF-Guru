<template>
    <div>
        <a-form ref="formRef" style="border: 1px solid #dddddd; padding: 10px 0;border-radius: 10px;margin-right: 5vw;"
            :model="store" :label-col="{ span: 3 }" :wrapper-col="{ offset: 1, span: 18 }" :rules="rules" @finish="onFinish"
            @finishFailed="onFinishFailed">
            <a-form-item name="op" label="操作">
                <a-radio-group button-style="solid" v-model:value="store.op">
                    <a-radio-button value="extract">提取书签</a-radio-button>
                    <a-radio-button value="write">写入书签</a-radio-button>
                    <a-radio-button value="transform">转换书签</a-radio-button>
                    <a-radio-button value="recognize">识别书签</a-radio-button>
                </a-radio-group>
            </a-form-item>
            <div v-if="store.op == 'extract'">
                <a-form-item name="bookmark.extract_format" label="导出格式">
                    <a-select v-model:value="store.extract_format" style="width: 200px">
                        <a-select-option value="txt">txt</a-select-option>
                        <a-select-option value="json">json</a-select-option>
                    </a-select>
                </a-form-item>
            </div>
            <div v-if="store.op == 'write'">
                <a-form-item name="bookmark.write_type" label="类型">
                    <a-radio-group v-model:value="store.write_type">
                        <a-radio value="file">书签文件导入</a-radio>
                        <a-radio value="page">页码书签</a-radio>
                    </a-radio-group>
                </a-form-item>
                <a-form-item name="bookmark_file" label="书签文件" :validateStatus="validateStatus.bookmark_file"
                    :help="validateHelp.bookmark_file" v-if="store.write_type == 'file'">
                    <div>
                        <a-row>
                            <a-col :span="22">
                                <a-input v-model:value="store.bookmark_file" placeholder="书签文件路径" allow-clear />
                            </a-col>
                            <a-col :span="1" style="margin-left: 1vw;">
                                <a-tooltip>
                                    <template #title>选择文件</template>
                                    <a-button @click="selectFile('bookmark_file')"><ellipsis-outlined /></a-button>
                                </a-tooltip>
                            </a-col>
                        </a-row>
                    </div>
                </a-form-item>
                <a-form-item name="write_offset" label="页码偏移量" v-if="store.write_type == 'file'">
                    <a-input-number v-model:value="store.write_offset" />
                </a-form-item>
                <a-form-item name="page" label="页码范围" hasFeedback :validateStatus="validateStatus.page"
                    :help="validateHelp.page">
                    <a-input v-model:value="store.page" placeholder="e.g. 3-N (留空表示全部页面)" allow-clear />
                </a-form-item>
                <a-form-item name="write_gap" label="间隔页数" v-if="store.write_type == 'page'">
                    <a-input-number v-model:value="store.write_gap" />
                </a-form-item>
                <a-form-item name="start_number" label="起始编号" v-if="store.write_type == 'page'">
                    <a-input-number v-model:value="store.start_number" />
                </a-form-item>
                <a-form-item name="bookmark.write_format" label="命名格式" v-if="store.write_type == 'page'">
                    <a-input v-model:value="store.write_format" placeholder="e.g. 第%p页(%p表示页码)" allow-clear />
                </a-form-item>
            </div>
            <div v-if="store.op == 'transform'">
                <a-form-item name="transform_offset" label="页码偏移量">
                    <a-input-number v-model:value="store.transform_offset" />
                </a-form-item>
                <div>
                    <a-form-item :label="index === 0 ? '缩进层级设置' : ' '" :colon="index === 0 ? true : false"
                        v-for="(item, index) in indentItems.items" :key="index">
                        <a-space>
                            <a-select v-model:value="indentItems.items[index].type" style="width: 200px"
                                placeholder="选择标题前缀" @change="selectChange(index)">
                                <a-select-option value="第一章">第一章</a-select-option>
                                <a-select-option value="第一节">第一节</a-select-option>
                                <a-select-option value="第一小节">第一小节</a-select-option>
                                <a-select-option value="第一编">第一编</a-select-option>
                                <a-select-option value="第一卷">第一卷</a-select-option>
                                <a-select-option value="第一部分">第一部分</a-select-option>
                                <a-select-option value="第一课">第一课</a-select-option>
                                <a-select-option value="一、">一、</a-select-option>
                                <a-select-option value="1">1</a-select-option>
                                <a-select-option value="1.1">1.1</a-select-option>
                                <a-select-option value="1.1.1">1.1.1</a-select-option>
                                <a-select-option value="1.1.1.1">1.1.1.1</a-select-option>
                                <a-select-option value="Chapter 1">Chapter 1</a-select-option>
                                <a-select-option value="Lesson 1">Lesson 1</a-select-option>
                                <a-select-option value="custom">自定义</a-select-option>
                            </a-select>
                            <a-input v-model:value="indentItems.items[index].prefix"
                                v-if="indentItems.items[index].type === 'custom'" style="width: 280px"
                                placeholder="自定义前缀(支持正则), e.g. 第.+小节" allow-clear />
                            <a-select v-model:value="indentItems.items[index].level" style="width: 200px"
                                placeholder="选择标题层级">
                                <a-select-option value="1">1</a-select-option>
                                <a-select-option value="2">2</a-select-option>
                                <a-select-option value="3">3</a-select-option>
                                <a-select-option value="4">4</a-select-option>
                                <a-select-option value="5">5</a-select-option>
                                <a-select-option value="6">6</a-select-option>
                            </a-select>
                        </a-space>
                        <MinusCircleOutlined @click="removeIndentItem(item)" style="margin-left: 1vw;" />
                    </a-form-item>
                    <a-form-item name="span" :label="indentItems.items.length === 0 ? '缩进层级设置' : ' '"
                        :colon="indentItems.items.length === 0 ? true : false">
                        <a-button type="dashed" block @click="addIndentItem" style="width: 410px;">
                            <PlusOutlined />
                            添加层级
                        </a-button>
                    </a-form-item>
                </div>
                <a-form-item label="默认层级">
                    <a-input-number v-model:value="store.default_level" :min="1"></a-input-number>
                </a-form-item>
                <a-form-item label="删除标题层级">
                    <a-select v-model:value="store.delete_level_below" style="width: 200px">
                        <a-select-option :value="0">无</a-select-option>
                        <a-select-option :value="2">二级标题及以下</a-select-option>
                        <a-select-option :value="3">三级标题及以下</a-select-option>
                        <a-select-option :value="4">四级标题及以下</a-select-option>
                        <a-select-option :value="5">五级标题及以下</a-select-option>
                        <a-select-option :value="6">六级标题及以下</a-select-option>
                    </a-select>
                </a-form-item>
                <a-form-item label="删除空行">
                    <a-switch v-model:checked="store.remove_blank_lines" />
                </a-form-item>
            </div>
            <div v-if="store.op == 'recognize'">
                <a-form-item name="bookmark.recognize_type" label="类型">
                    <a-radio-group v-model:value="store.recognize_type">
                        <a-radio value="font">基于字体属性</a-radio>
                        <a-radio value="ocr">基于OCR <a-tag color="blue">python</a-tag></a-radio>
                    </a-radio-group>
                </a-form-item>
                <div v-if="store.recognize_type == 'ocr'">
                    <a-form-item name="bookmark.ocr_lang" label="语言">
                        <a-select v-model:value="store.ocr_lang" style="width: 200px">
                            <a-select-option value="ch">简体中文</a-select-option>
                            <a-select-option value="en">英文 </a-select-option>
                        </a-select>
                    </a-form-item>
                    <a-form-item name="bookmark.ocr_double_column" label="双栏">
                        <a-switch v-model:checked="store.ocr_double_column" />
                    </a-form-item>
                    <a-form-item name="page" label="目录页码范围" hasFeedback :validateStatus="validateStatus.page"
                        :help="validateHelp.page">
                        <a-input v-model:value="store.page" placeholder="e.g. 1-10,11-15,16-19" allow-clear />
                    </a-form-item>
                </div>
                <div v-if="store.recognize_type == 'font'">
                    <a-form-item name="page" label="检索页码范围" hasFeedback :validateStatus="validateStatus.page"
                        :help="validateHelp.page">
                        <a-input v-model:value="store.page" placeholder="e.g. 3-N" allow-clear />
                    </a-form-item>
                    <a-form-item name="input" label="输入" :validateStatus="validateStatus.input" :help="validateHelp.input">
                        <div>
                            <a-row>
                                <a-col :span="22">
                                    <a-input v-model:value="store.input"
                                        placeholder="含有使用矩形注释标注标题层级的输入文件路径, 支持使用*匹配多个文件, 如D:\test\*.pdf" allow-clear />
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
                </div>
            </div>
            <a-form-item name="input" label="输入" :validateStatus="validateStatus.input" :help="validateHelp.input"
                v-if="!(store.op === 'recognize' && store.recognize_type === 'font')">
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
        <!-- <div v-if="store.op === 'recognize' && store.recognize_type === 'font'" style="margin-top: 1vh;width: 85%;">
            <a-alert message="请确保输入文件中含有标注了标题层级的矩形注释" type="info" show-icon />
        </div> -->
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
    ExtractBookmark,
    WriteBookmarkByFile,
    TransformBookmark,
    WriteBookmarkByGap,
    OCRPDFBookmark,
    DetectBookmarkByFont,
} from '../../../wailsjs/go/main/App';
import type { FormInstance } from 'ant-design-vue';
import type { Rule } from 'ant-design-vue/es/form';
import { MinusCircleOutlined, PlusOutlined, EllipsisOutlined } from '@ant-design/icons-vue';
import { handleOps } from "../data";
import { useBookmarkState } from '../../store/bookmark';

interface IndentItem {
    prefix: string | undefined;
    level: string | undefined;
    type: string | undefined;
}

export default defineComponent({
    components: {
        MinusCircleOutlined,
        PlusOutlined,
        EllipsisOutlined
    },
    setup() {
        const formRef = ref<FormInstance>();
        const store = useBookmarkState();

        const indentItems = reactive<{ items: IndentItem[] }>({
            items: [],
        })
        const addIndentItem = () => {
            indentItems.items.push({
                prefix: undefined,
                level: undefined,
                type: undefined,
            });
        };
        const removeIndentItem = (item: IndentItem) => {
            let index = indentItems.items.indexOf(item);
            if (index > -1) {
                indentItems.items.splice(index, 1);
            }
        };
        const selectChange = (index: number) => {
            if (indentItems.items[index].type !== 'custom') {
                indentItems.items[index].prefix = indentItems.items[index].type;
            } else {
                indentItems.items[index].prefix = undefined;
            }
        };
        const validateStatus = reactive({
            input: "",
            page: "",
            bookmark_file: "",
        });
        const validateHelp = reactive({
            input: "",
            page: "",
            bookmark_file: "",
        })
        const validateFileExists = async (_rule: Rule, value: string) => {
            console.log(_rule);
            console.log(value);
            // @ts-ignore
            validateStatus[_rule.field] = 'validating';
            if (value === '') {
                // @ts-ignore
                validateStatus[_rule.field] = 'error';
                // @ts-ignore
                validateHelp[_rule.field] = "请填写路径";
                return Promise.reject();
            }
            await CheckFileExists(value).then((res: any) => {
                console.log({ res });
                if (res) {
                    // @ts-ignore
                    validateStatus[_rule.field] = 'error';
                    // @ts-ignore
                    validateHelp[_rule.field] = res;
                    return Promise.reject();
                }
                // @ts-ignore
                validateStatus[_rule.field] = 'success';
                // @ts-ignore
                validateHelp[_rule.field] = res;
                return Promise.resolve();
            }).catch((err: any) => {
                console.log({ err });
                // @ts-ignore
                validateStatus[_rule.field] = 'error';
                // @ts-ignore
                validateHelp[_rule.field] = err;
                return Promise.reject("文件不存在");
            });
            // const legal_suffix = [".pdf"];
            // if (!legal_suffix.some((suffix) => value.trim().toLocaleLowerCase().endsWith(suffix))) {
            //     validateStatus["input"] = 'error';
            //     validateHelp["input"] = "仅支持pdf格式的文件";
            //     return Promise.reject();
            // }
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
            bookmark_file: [{ required: true, validator: validateFileExists, trigger: 'change' }],
            write_offset: [{ required: true, message: "请填写页码偏移量, 计算方式：实际页码-标注页码" }],
            write_gap: [{ required: true, message: "请填写间隔页数" }],
            transform_offset: [{ required: true, message: "增减页码的数值" }],
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
                case "extract": {
                    await handleOps(ExtractBookmark, [store.input, store.output, store.extract_format]);
                    break;
                }
                case "write": {
                    switch (store.write_type) {
                        case "file": {
                            await handleOps(WriteBookmarkByFile, [store.input, store.output, store.bookmark_file, store.write_offset]);
                            break;
                        }
                        case "page": {
                            await handleOps(WriteBookmarkByGap, [store.input, store.output, store.write_gap, store.write_format, store.start_number, store.page]);
                            break;
                        }
                    }
                    break;
                }
                case "transform": {
                    let items = indentItems.items.filter((item) => {
                        return item.prefix !== undefined && item.level !== undefined;
                    });
                    let res = [];
                    for (let i = 0; i < items.length; i++) {
                        res.push(`{"prefix":"${items[i].prefix}","level":"${items[i].level}", "type":"${items[i].type}"}`);
                    }
                    console.log(res);
                    await handleOps(TransformBookmark, [store.input, store.output, store.transform_offset, res, store.delete_level_below, store.default_level, store.remove_blank_lines]);
                    break;
                }
                case "recognize": {
                    switch (store.recognize_type) {
                        case "font": {
                            await handleOps(DetectBookmarkByFont, [store.input, store.output, store.page]);
                            break;
                        }
                        case "ocr": {
                            await handleOps(OCRPDFBookmark, [store.input, store.output, store.page, store.ocr_lang, store.ocr_double_column]);
                            break;
                        }
                    }

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
            indentItems,
            addIndentItem,
            removeIndentItem,
            selectChange,
        };
    }
})
</script>