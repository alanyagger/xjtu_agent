import axios from 'axios';
import { ElMessage } from 'element-plus';
import { useRouter } from 'vue-router';

const router = useRouter();

const request = axios.create({
  baseURL: '/api', // 与后端跨域代理对应（看vite.config.ts）
  timeout: 5000,
});

// 请求拦截器：加Token
request.interceptors.request.use(
  (config) => {
    const token = localStorage.getItem('token');
    if (token) {
      config.headers.Authorization = `Bearer ${token}`;
    }
    return config;
  },
  (error) => Promise.reject(error)
);

// 响应拦截器：处理401（未登录）
request.interceptors.response.use(
  (response) => response.data,
  (error) => {
    if (error.response?.status === 401) {
      ElMessage.error('请登录');
      router.push('/login');
    } else {
      ElMessage.error(error.response?.data?.detail || '请求失败');
    }
    return Promise.reject(error);
  }
);

export default request;