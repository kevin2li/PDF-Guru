import { createApp } from 'vue';
import App from './App.vue';
import { createPinia } from "pinia";
import Antd from "ant-design-vue";
import "ant-design-vue/dist/antd.css";

const app = createApp(App);
const pinia = createPinia();
app.use(pinia);
app.use(Antd);
app.mount("#app");
