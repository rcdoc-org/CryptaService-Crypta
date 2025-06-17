import axios from 'axios';

const authApi = axios.create({
    baseURL: import.meta.env.VITE_AUTH_URL || '/api/v1/auth',
    headers: { 'Content-Type': 'application/json' },
});

export const register = (data) => authApi.post('/register', data);
export const login = (data) => authApi.post('/login', data);
export const oauthLogin = (provider) => {
    window.location.href = `${authApi.defaults.baseURL}/${provider}/login`;
};

export default authApi;