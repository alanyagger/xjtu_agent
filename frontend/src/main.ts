import { createApp } from "vue";
import "@/assets/style/main.css";
import App from "./App.vue";
const app = createApp(App);

// 引入 element-ui 库
import ElementPlus from "element-plus";
import "element-plus/dist/index.css";
import zhCn from "element-plus/dist/locale/zh-cn.mjs";
app.use(ElementPlus, {
  locale: zhCn,
});

// 引入 element 图标库
import * as ElementPlusIconsVue from "@element-plus/icons-vue";
for (const [key, component] of Object.entries(ElementPlusIconsVue)) {
  app.component(key, component);
}

// 安装路由插件
import router from "./router";
app.use(router);

import Antd from 'ant-design-vue';
import 'ant-design-vue/dist/reset.css'; 
app.use(Antd); 

// md 预览相关配置
import VMdPreview from "@kangc/v-md-editor/lib/preview";
import "@kangc/v-md-editor/lib/style/preview.css";
import githubTheme from "@kangc/v-md-editor/lib/theme/github.js";
import "@kangc/v-md-editor/lib/theme/style/github.css";
// md 复制插件
import createCopyCodePlugin from "@kangc/v-md-editor/lib/plugins/copy-code/index";
import "@kangc/v-md-editor/lib/plugins/copy-code/copy-code.css";
// highlightjs
import hljs from "highlight.js";

VMdPreview.use(githubTheme, {
  Hljs: hljs,
});
VMdPreview.use(createCopyCodePlugin());
app.use(VMdPreview);

app.mount("#app");