<template>
    <a-form ref="formRef" name="custom-validation" :model="formState" :rules="rules" v-bind="layout" @finish="handleFinish"
        @validate="handleValidate" @finishFailed="handleFinishFailed">
        <a-form-item name="encrypt_op" label="操作" style="margin-bottom: 1.8vh;">
            <a-radio-group button-style="solid" v-model:value="formState.op">
                <a-radio-button value="encrypt">加密</a-radio-button>
                <a-radio-button value="decrypt">解密</a-radio-button>
            </a-radio-group>
        </a-form-item>
        <a-form-item name="upw" label="设置密码" hasFeedback :validateStatus="validateStatus.encrypt_upw">
            <a-input-password v-model:value="formState.upw" placeholder="不少于6位" allow-clear />
        </a-form-item>
        <a-form-item name="pass" label="Password"  hasFeedback :validateStatus="validateStatus.encrypt_upw">
            <a-input-password v-model:value="formState.pass" placeholder="不少于6位" allow-clear />
        </a-form-item>
        <!-- <a-form-item has-feedback label="Password" name="pass">
            <a-input-password v-model:value="formState.pass" type="password" autocomplete="off" />
        </a-form-item> -->
        <a-form-item has-feedback label="Confirm" name="checkPass">
            <a-input v-model:value="formState.checkPass" type="password" autocomplete="off" />
        </a-form-item>
        <a-form-item has-feedback label="Age" name="age">
            <a-input-number v-model:value="formState.age" />
        </a-form-item>
        <a-form-item :wrapper-col="{ span: 14, offset: 4 }">
            <a-button type="primary" html-type="submit">Submit</a-button>
            <a-button style="margin-left: 10px" @click="resetForm">Reset</a-button>
        </a-form-item>
    </a-form>
</template>
<script lang="ts">
import type { Rule } from 'ant-design-vue/es/form';
import { defineComponent, reactive, ref } from 'vue';
import type { FormInstance } from 'ant-design-vue';
interface FormState {
    op: string,
    is_set_upw: boolean,
    upw: string,
    upw_confirm: string,
    pass: string;
    checkPass: string;
    age: number | undefined;
}
export default defineComponent({
    setup() {
        const formRef = ref<FormInstance>();
        const formState = reactive<FormState>({
            op: 'encrypt',
            is_set_upw: false,
            upw: '',
            upw_confirm: '',
            pass: '',
            checkPass: '',
            age: undefined,
        });
        const validateStatus = reactive({
            input: "",
            encrypt_upw: '',
            encrypt_upw_confirm: '',
            encrypt_opw: '',
            encrypt_opw_confirm: '',
        });
        let checkAge = async (_rule: Rule, value: number) => {
            if (!value) {
                return Promise.reject('Please input the age');
            }
            if (!Number.isInteger(value)) {
                return Promise.reject('Please input digits');
            } else {
                if (value < 18) {
                    return Promise.reject('Age must be greater than 18');
                } else {
                    return Promise.resolve();
                }
            }
        };
        let validatePass = async (_rule: Rule, value: string) => {
            console.log({ _rule });
            console.log({ value });
            if (value === '') {
                return Promise.reject('Please input the password');
            } else {
                if (formState.checkPass !== '') {
                    // @ts-ignore
                    formRef.value.validateFields('checkPass');
                }
                return Promise.resolve();
            }
        };
        let validatePass2 = async (_rule: Rule, value: string) => {
            if (value === '') {
                return Promise.reject('Please input the password again');
            } else if (value !== formState.pass) {
                return Promise.reject("Two inputs don't match!");
            } else {
                return Promise.resolve();
            }
        };
        let validatePassUpw = async (_rule: Rule, value: string) => {
            validateStatus["encrypt_upw"] = 'validating';
            if (value === '') {
                validateStatus["encrypt_upw"] = 'error';
                return Promise.reject('请输入密码');
            } else {
                if (value.length < 6) {
                    validateStatus["encrypt_upw"] = 'error';
                    return Promise.reject('密码长度不能少于6位');
                }
                validateStatus["encrypt_upw"] = 'success';
                return Promise.resolve();
            }
        };
        const rules: Record<string, Rule[]> = {
            // pass: [{ required: true, validator: validatePass, trigger: 'change' }],
            pass: [{ required: true, validator: validatePassUpw, trigger: 'change' }],
            checkPass: [{ validator: validatePass2, trigger: 'change' }],
            age: [{ validator: checkAge, trigger: 'change' }],
            upw: [{ required: true, validator: validatePassUpw, trigger: 'change' }],
        };
        const layout = {
            labelCol: { span: 4 },
            wrapperCol: { span: 14 },
        };
        const handleFinish = (values: FormState) => {
            console.log(values, formState);
        };
        const handleFinishFailed = (errors: any) => {
            console.log(errors);
        };
        const resetForm = () => {
            // @ts-ignore
            formRef.value.resetFields();
        };
        // @ts-ignore
        const handleValidate = (...args) => {
            console.log(args);
        };
        return {
            formState,
            formRef,
            rules,
            layout,
            handleFinishFailed,
            handleFinish,
            resetForm,
            handleValidate,
            validateStatus
        };
    },
});
</script>