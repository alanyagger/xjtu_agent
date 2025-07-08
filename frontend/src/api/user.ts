import request from '@/utils/request';

// 注册参数
interface RegisterData {
  username: string;
  email: string;
  password: string;
}

// 登录参数（与OAuth2PasswordRequestForm对应）
interface LoginData {
  username: string;
  password: string;
}

export const userApi = {
  register: (data: RegisterData) => request.post('/register', data),
  login: (data: LoginData) => request.post('/token', data), // 注意：后端/token需要form-data
};