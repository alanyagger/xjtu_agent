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

// export const userApi = {
//   register: (data: RegisterData) => request.post('/register', data),
//   login: (data: LoginData) => request.post('/token', data), // 注意：后端/token需要form-data
// };

export const userApi = {
  register: (data: RegisterData) => request.post('/register', data),
  
  // 登录接口：使用表单格式
  login: (data: LoginData) => {
    // 将参数转为表单格式
    const formData = new URLSearchParams();
    formData.append('username', data.username);
    formData.append('password', data.password);
    
    // 发送请求时指定 Content-Type
    return request.post('/token', formData, {
      headers: {
        'Content-Type': 'application/x-www-form-urlencoded'
      }
    });
  }
};