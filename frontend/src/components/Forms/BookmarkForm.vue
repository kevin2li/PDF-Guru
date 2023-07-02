<template>
    <div>
        <a-form ref="formRef" style="border: 1px solid #dddddd; padding: 10px 0;border-radius: 10px;margin-right: 5vw;"
            :model="formState" :label-col="{ span: 3 }" :wrapper-col="{ offset: 1, span: 18 }" :rules="rules">
            <a-form-item name="bookmark_op" label="操作">
                <a-radio-group button-style="solid" v-model:value="formState.op">
                    <a-radio-button value="extract">提取书签</a-radio-button>
                    <a-radio-button value="write">写入书签</a-radio-button>
                    <a-radio-button value="transform">转换书签</a-radio-button>
                    <a-radio-button value="recognize">识别书签</a-radio-button>
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
                <a-form-item name="bookmark.write_type" label="类型" :rules="{ required: true }">
                    <a-radio-group v-model:value="formState.write_type">
                        <a-radio value="file">书签文件导入</a-radio>
                        <a-radio value="page">页码书签</a-radio>
                    </a-radio-group>
                </a-form-item>
                <a-form-item name="bookmark_file" label="书签文件" hasFeedback :validateStatus="validateStatus.bookmark_file"
                    :help="validateHelp.bookmark_file" v-if="formState.write_type == 'file'">
                    <a-input v-model:value="formState.bookmark_file" placeholder="书签文件路径" allow-clear />
                </a-form-item>
                <a-form-item name="bookmark.write_offset" label="页码偏移量" :rules="{ required: true }"
                    v-if="formState.write_type == 'file'">
                    <a-input-number v-model:value="formState.write_offset" placeholder="页码偏移量" />
                </a-form-item>
                <a-form-item name="bookmark.write_gap" label="间隔页数" :rules="{ required: true }"
                    v-if="formState.write_type == 'page'">
                    <a-input-number v-model:value="formState.write_gap" placeholder="间隔页数" />
                </a-form-item>
                <a-form-item name="bookmark.write_format" label="命名格式" v-if="formState.write_type == 'page'">
                    <a-input v-model:value="formState.write_format" placeholder="e.g. 第%p页(%p表示页码)" allow-clear />
                </a-form-item>
            </div>
            <div v-if="formState.op == 'transform'">
                <a-form-item name="bookmark.transform_offset" label="页码偏移量" :rules="{ required: true }">
                    <a-input-number v-model:value="formState.transform_offset" placeholder="页码偏移量" />
                </a-form-item>
                <a-form-item name="bookmark.transform_indent" label="增加缩进" :rules="{ required: true }">
                    <a-switch v-model:checked="formState.transform_indent" />
                </a-form-item>
                <a-form-item name="bookmark.transform_dots" label="删除尾部点" :rules="{ required: true }">
                    <a-switch v-model:checked="formState.transform_dots" />
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
                <a-button type="primary" html-type="submit" @click="onSubmit" :loading="confirmLoading">确认</a-button>
                <a-button style="margin-left: 10px" @click="resetFields">重置</a-button>
            </a-form-item>
        </a-form>
    </div>
</template>
<script lang="ts">
import { defineComponent, reactive, watch, ref } from 'vue';
import { message, Modal } from 'ant-design-vue';
import { CheckFileExists, CheckRangeFormat, ExtractBookmark, WriteBookmarkByFile, TransformBookmark, WriteBookmarkByGap } from '../../../wailsjs/go/main/App';
import type { FormInstance } from 'ant-design-vue';
import type { Rule } from 'ant-design-vue/es/form';
import type { BookmarkState } from "../data";
import { handleOps } from "../data";
export default defineComponent({
    components: {
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
        });

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
                        await handleOps(TransformBookmark, [formState.input, formState.output, formState.transform_indent, formState.transform_offset, formState.transform_dots]);
                        break;
                    }
                }
                confirmLoading.value = false;
            } catch (err) {
                console.log({ err });
                message.error("表单验证失败");
            }
        }
        return { formState, rules, formRef, validateStatus, validateHelp, confirmLoading, resetFields, onSubmit };
    }
})
</script>