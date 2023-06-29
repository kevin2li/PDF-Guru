<template>
    <div>

    </div>
</template>

<script lang="ts">

import { ref, defineComponent } from "vue";
import { UploadOutlined } from '@ant-design/icons-vue';
export default defineComponent({
    components: { UploadOutlined, },
    setup() {
        const msg = ref("Hello, vue3");
        const count = ref(1);
        const add = () => {
            count.value++;
        };
        const value = ref(1);

        return {
            add,
            count,
            msg,
            value,
        };
    },
});
</script>