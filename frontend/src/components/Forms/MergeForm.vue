<template>
    <div>
        <a-form ref="formRef" style="border: 1px solid #dddddd; padding: 10px 0;border-radius: 10px;margin-right: 5vw;"
            :model="store" :label-col="{ span: 3 }" :wrapper-col="{ offset: 1, span: 18 }" :rules="rules" @finish="onFinish"
            @finishFailed="onFinishFailed">
            <a-form-item :label="index === 0 ? '输入路径列表' : ' '" :colon="index === 0 ? true : false"
                :help="validateHelp.input_path_list[index]" :rules="[{ validator: validateFileExists, trigger: 'change' }]"
                v-for="(item, index) in store.input_path_list" :key="index">
                <a-input v-model:value="store.input_path_list[index]" style="width: 90%;" allow-clear
                    placeholder="待合并pdf文件路径" />
                <MinusCircleOutlined @click="removePath(item)" style="margin-left: 1vw;" />
            </a-form-item>
            <a-form-item name="span" :label="store.input_path_list.length === 0 ? '输入路径列表' : ' '"
                :colon="store.input_path_list.length === 0 ? true : false">
                <a-button type="dashed" block @click="addPath">
                    <PlusOutlined />
                    添加路径
                </a-button>
            </a-form-item>
            <a-form-item name="merge.sort" label="排序字段">
                <a-radio-group v-model:value="store.sort">
                    <a-radio value="default">添加顺序</a-radio>
                    <a-radio value="name">文件名(字母)</a-radio>
                    <a-radio value="name_digit">文件名(编号)</a-radio>
                    <a-radio value="ctime">创建时间</a-radio>
                    <a-radio value="mtime">修改时间</a-radio>
                </a-radio-group>
            </a-form-item>
            <a-form-item label="排序方向">
                <a-radio-group v-model:value="store.sort_direction">
                    <a-radio value="asc">升序</a-radio>
                    <a-radio value="desc">降序</a-radio>
                </a-radio-group>
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
import { defineComponent, reactive, ref } from 'vue';
import { message, Modal } from 'ant-design-vue';
import {
    SelectFile,
    SaveFile,
    SelectMultipleFiles,
    CheckFileExists,
    CheckRangeFormat,
    MergePDF
} from '../../../wailsjs/go/main/App';
import type { FormInstance } from 'ant-design-vue';
import type { Rule } from 'ant-design-vue/es/form';
import { MinusCircleOutlined, PlusOutlined, EllipsisOutlined } from '@ant-design/icons-vue';
import { handleOps } from "../data";
import { useMergeState } from '../../store/merge';
export default defineComponent({
    components: {
        MinusCircleOutlined,
        PlusOutlined,
        EllipsisOutlined
    },
    setup() {
        const formRef = ref<FormInstance>();
        const store = useMergeState();

        const validateStatus = reactive({
            input_path_list: [],
            page: "",
        });
        const validateHelp = reactive({
            input_path_list: [],
            page: "",
        });
        const validateFileExists = async (_rule: Rule, value: string) => {
            console.log(_rule);
            console.log(value);
            // @ts-ignore
            // const index = _rule.field.split("_").at(-1);
            const index = 0;
            // @ts-ignore
            validateStatus["input_path_list"][index] = 'validating';
            if (value === '') {
                // @ts-ignore
                validateStatus["input_path_list"][index] = 'error';
                // @ts-ignore
                validateHelp["input_path_list"][index] = '请填写路径';
                return Promise.reject();
            }
            await CheckFileExists(value).then((res: any) => {
                console.log({ res });
                if (res) {
                    // @ts-ignore
                    validateStatus["input_path_list"][index] = 'error';
                    // @ts-ignore
                    validateHelp["input_path_list"][index] = res;
                    return Promise.reject();
                }
                // @ts-ignore
                validateStatus["input_path_list"][index] = 'success';
                // @ts-ignore
                validateHelp["input_path_list"][index] = "";
                return Promise.resolve();
            }).catch((err: any) => {
                console.log({ err });
                // @ts-ignore
                validateStatus["input_path_list"][index] = 'error';
                // @ts-ignore
                validateHelp["input_path_list"][index] = err;
                return Promise.reject("文件不存在");
            });
            const legal_suffix = [".pdf"];
            if (!legal_suffix.some((suffix) => value.endsWith(suffix))) {
                // @ts-ignore
                validateStatus["input_path_list"][index] = 'error';
                // @ts-ignore
                validateHelp["input_path_list"][index] = "仅支持pdf格式的文件";
                return Promise.reject();
            }
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
        // 合并PDF
        const addPath = async () => {
            await SelectMultipleFiles().then((res: any) => {
                console.log({ res });
                if (res) {
                    store.input_path_list.push(...res);
                }
                formRef.value?.validateFields("input_path_list");
                for (let i = 0; i < res.length; i++) {
                    // @ts-ignore
                    validateStatus.input_path_list.push("");
                    // @ts-ignore
                    validateHelp.input_path_list.push("");
                }
            }).catch((err: any) => {
                console.log({ err });
            });
        }
        const removePath = (item: string) => {
            const index = store.input_path_list.indexOf(item);
            if (index != -1) {
                store.input_path_list.splice(index, 1);
                // @ts-ignore
                validateStatus.input_path_list.splice(index, 1);
                // @ts-ignore
                validateHelp.input_path_list.splice(index, 1);
            }
        }
        // 重置表单
        const resetFields = () => {
            formRef.value?.clearValidate();
            store.resetState();
        }
        // 提交表单
        const confirmLoading = ref<boolean>(false);
        async function submit() {
            confirmLoading.value = true;
            await handleOps(MergePDF, [store.input_path_list, store.output, store.sort, store.sort_direction]);
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
        const selectMultipleFiles = async () => {
            await SelectMultipleFiles().then((res: any) => {
                console.log({ res });
            }).catch((err: any) => {
                console.log({ err });
            });
        }
        return {
            selectFile,
            saveFile,
            selectMultipleFiles,
            store,
            rules,
            formRef,
            validateStatus,
            validateHelp,
            validateFileExists,
            confirmLoading,
            addPath,
            removePath,
            resetFields,
            onFinish,
            onFinishFailed
        };
    }
})
</script>