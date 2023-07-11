<template>
    <div>
        <a-form ref="formRef" style="border: 1px solid #dddddd; padding: 10px 0;border-radius: 10px;margin-right: 5vw;"
            :model="formState" :label-col="{ span: 3 }" :wrapper-col="{ offset: 1, span: 18 }" :rules="rules"
            @finish="onFinish" @finishFailed="onFinishFailed">
            <a-form-item name="bookmark_op" label="操作">
                <a-radio-group button-style="solid" v-model:value="formState.op">
                    <a-radio-button value="extract">提取书签</a-radio-button>
                    <a-radio-button value="write">写入书签</a-radio-button>
                    <a-radio-button value="transform">转换书签</a-radio-button>
                    <a-radio-button value="recognize">
                        <a-space>
                            <span>识别书签</span>
                            <a-tag color="blue">python</a-tag>
                        </a-space>
                    </a-radio-button>
                </a-radio-group>
            </a-form-item>
            <div v-if="formState.op == 'extract'">
                <a-form-item name="bookmark.extract_format" label="导出格式">
                    <a-select v-model:value="formState.extract_format" style="width: 200px">
                        <a-select-option value="txt">txt</a-select-option>
                        <a-select-option value="json">json</a-select-option>
                    </a-select>
                </a-form-item>
            </div>
            <div v-if="formState.op == 'write'">
                <a-form-item name="bookmark.write_type" label="类型">
                    <a-radio-group v-model:value="formState.write_type">
                        <a-radio value="file">书签文件导入</a-radio>
                        <a-radio value="page">页码书签</a-radio>
                    </a-radio-group>
                </a-form-item>
                <a-form-item name="bookmark_file" label="书签文件" hasFeedback :validateStatus="validateStatus.bookmark_file"
                    :help="validateHelp.bookmark_file" v-if="formState.write_type == 'file'">
                    <a-input v-model:value="formState.bookmark_file" placeholder="书签文件路径" allow-clear />
                </a-form-item>
                <a-form-item name="write_offset" label="页码偏移量" v-if="formState.write_type == 'file'">
                    <a-input-number v-model:value="formState.write_offset" />
                </a-form-item>
                <a-form-item name="write_gap" label="间隔页数" v-if="formState.write_type == 'page'">
                    <a-input-number v-model:value="formState.write_gap" />
                </a-form-item>
                <a-form-item name="bookmark.write_format" label="命名格式" v-if="formState.write_type == 'page'">
                    <a-input v-model:value="formState.write_format" placeholder="e.g. 第%p页(%p表示页码)" allow-clear />
                </a-form-item>
            </div>
            <div v-if="formState.op == 'transform'">
                <a-form-item name="transform_offset" label="页码偏移量">
                    <a-input-number v-model:value="formState.transform_offset" />
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
                    <a-input-number v-model:value="formState.default_level" :min="1"></a-input-number>
                </a-form-item>
                <a-form-item label="删除标题层级">
                    <a-select v-model:value="formState.delete_level_below" style="width: 200px">
                        <a-select-option :value="0">无</a-select-option>
                        <a-select-option :value="2">二级标题及以下</a-select-option>
                        <a-select-option :value="3">三级标题及以下</a-select-option>
                        <a-select-option :value="4">四级标题及以下</a-select-option>
                        <a-select-option :value="5">五级标题及以下</a-select-option>
                        <a-select-option :value="6">六级标题及以下</a-select-option>
                    </a-select>
                </a-form-item>
                <a-form-item label="删除空行">
                    <a-switch v-model:checked="formState.remove_blank_lines" />
                </a-form-item>
            </div>
            <div v-if="formState.op == 'recognize'">
                <a-form-item name="bookmark.ocr_lang" label="语言">
                    <a-select v-model:value="formState.ocr_lang" style="width: 200px">
                        <a-select-option value="ch">简体中文</a-select-option>
                        <a-select-option value="en">英文</a-select-option>
                    </a-select>
                </a-form-item>
                <a-form-item name="bookmark.ocr_double_column" label="双栏">
                    <a-switch v-model:checked="formState.ocr_double_column" />
                </a-form-item>
                <a-form-item name="page" label="目录页码范围" hasFeedback :validateStatus="validateStatus.page"
                    :help="validateHelp.page">
                    <a-input v-model:value="formState.page" placeholder="e.g. 1-10,11-15,16-19" allow-clear />
                </a-form-item>
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
import {
    CheckFileExists,
    CheckRangeFormat,
    ExtractBookmark,
    WriteBookmarkByFile,
    TransformBookmark,
    WriteBookmarkByGap,
    OCRPDFBookmark,
} from '../../../wailsjs/go/main/App';
import type { FormInstance } from 'ant-design-vue';
import type { Rule } from 'ant-design-vue/es/form';
import { MinusCircleOutlined, PlusOutlined } from '@ant-design/icons-vue';
import type { BookmarkState } from "../data";
import { handleOps } from "../data";

interface IndentItem {
    prefix: string | undefined;
    level: string | undefined;
    type: string | undefined;
}

export default defineComponent({
    components: {
        MinusCircleOutlined,
        PlusOutlined,
    },
    setup() {
        const formRef = ref<FormInstance>();
        const formState = reactive<BookmarkState>({
            input: "",
            output: "",
            page: "",
            op: "extract",
            bookmark_file: "",
            write_type: "file",
            write_format: "",
            write_offset: 0,
            write_gap: 1,
            extract_format: "txt",
            transform_offset: 0,
            transform_indent: false,
            transform_dots: false,
            ocr_lang: "ch",
            ocr_double_column: false,
            delete_level_below: 0,
            default_level: 1,
            remove_blank_lines: true,
        });

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
            formRef.value?.resetFields();
        }
        // 提交表单
        const confirmLoading = ref<boolean>(false);
        async function submit() {
            confirmLoading.value = true;
            switch (formState.op) {
                case "extract": {
                    await handleOps(ExtractBookmark, [formState.input, formState.output, formState.extract_format]);
                    break;
                }
                case "write": {
                    switch (formState.write_type) {
                        case "file": {
                            await handleOps(WriteBookmarkByFile, [formState.input, formState.output, formState.bookmark_file, formState.write_offset]);
                            break;
                        }
                        case "page": {
                            await handleOps(WriteBookmarkByGap, [formState.input, formState.output, formState.write_gap, formState.write_format]);
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
                    await handleOps(TransformBookmark, [formState.input, formState.output, formState.transform_offset, res, formState.delete_level_below, formState.default_level, formState.remove_blank_lines]);
                    break;
                }
                case "recognize": {
                    await handleOps(OCRPDFBookmark, [formState.input, formState.output, formState.page, formState.ocr_lang, formState.ocr_double_column]);
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
        return {
            formState,
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