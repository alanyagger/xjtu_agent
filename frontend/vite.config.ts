import { defineConfig } from 'vite'
import vue from '@vitejs/plugin-vue'
import { fileURLToPath, URL } from "node:url";  // 保留原有导入

export default defineConfig({
  plugins: [vue()],  // 保留原有插件
  resolve: {
    alias: {
      "@": fileURLToPath(new URL("./src", import.meta.url)),  // 保留路径别名配置
    },
  },
  // 新增跨域代理配置（与原有配置同级）
  server: {
    proxy: {
      '/api': {
        target: 'http://localhost:8000',  // 后端启动地址（FastAPI默认端口8000）
        changeOrigin: true,  // 允许跨域
        rewrite: (path) => path.replace(/^\/api/, ''),  // 去掉请求路径中的/api前缀
      },
      '/chat': {
        target: 'http://localhost:8000', // 后端接口地址
        changeOrigin: true, // 允许跨域
        rewrite: (path) => path.replace(/^\/chat/, '/chat'), // 去掉请求路径中的/chat前缀
      },
    },
  },
});