<template>
    <div>
        <a-form ref="formRef" style="border: 1px solid #dddddd; padding: 10px 0;border-radius: 10px;margin-right: 5vw;"
            :model="formState" :label-col="{ span: 3 }" :wrapper-col="{ offset: 1, span: 18 }" :rules="rules">
            <a-form-item :label="index === 0 ? '输入路径列表' : ' '" :colon="index === 0 ? true : false" name="merge_input"
                v-for="(item, index) in formState.input_path_list" :key="index">
                <a-input v-model:value="formState.input_path_list[index]" style="width: 95%;" allow-clear
                    placeholder="待合并pdf文件路径" />
                <MinusCircleOutlined @click="removePath(item)" style="margin-left: 1vw;" />
            </a-form-item>
            <a-form-item name="span" :label="formState.input_path_list.length === 0 ? '输入路径列表' : ' '"
                :colon="formState.input_path_list.length === 0 ? true : false">
                <a-button type="dashed" block @click="addPath">
                    <PlusOutlined />
                    添加路径
                </a-button>
            </a-form-item>
            <a-form-item name="merge.sort" label="排序字段">
                <a-radio-group v-model:value="formState.sort">
                    <a-radio value="hand">添加顺序</a-radio>
                    <a-radio value="name">文件名</a-radio>
                    <a-radio value="create">创建时间</a-radio>
                    <a-radio value="modify">修改时间</a-radio>
                </a-radio-group>
            </a-form-item>
            <a-form-item label="排序方向">
                <a-radio-group v-model:value="formState.sort_direction">
                    <a-radio value="asc">升序</a-radio>
                    <a-radio value="desc">降序</a-radio>
                </a-radio-group>
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
import { CheckFileExists, CheckRangeFormat, MergePDF } from '../../../wailsjs/go/main/App';
import type { FormInstance } from 'ant-design-vue';
import type { Rule } from 'ant-design-vue/es/form';
import { MinusCircleOutlined, PlusOutlined } from '@ant-design/icons-vue';
import type { MergeState } from "../data";
import { handleOps } from "../data";
export default defineComponent({
    components: {
        MinusCircleOutlined,
        PlusOutlined,
    },
    setup() {
        const formRef = ref<FormInstance>();
        const formState = reactive<MergeState>({
            input_path_list: [],
            output: "",
            sort: "hand",
            sort_direction: "asc",
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
        // 合并PDF
        const addPath = () => {
            formState.input_path_list.push("");
        }
        const removePath = (item: string) => {
            const index = formState.input_path_list.indexOf(item);
            if (index != -1) {
                formState.input_path_list.splice(index, 1);
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
                await handleOps(MergePDF, [formState.input_path_list, formState.output, "create", false]);
                confirmLoading.value = false;
            } catch (err) {
                console.log({ err });
                message.error("表单验证失败");
            }
        }
        return { formState, rules, formRef, validateStatus, confirmLoading, addPath, removePath, resetFields, onSubmit };
    }
})
</script>