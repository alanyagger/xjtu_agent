// utils/auth.ts
export const getToken = (): string | null => {
    return localStorage.getItem('token');
};

// 配套的登录/登出函数
export const setToken = (token: string): void => {
    localStorage.setItem('token', token);
};

export const removeToken = (): void => {
    localStorage.removeItem('token');
};