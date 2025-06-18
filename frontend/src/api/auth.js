import axios from 'axios';

const authApi = axios.create({
    baseURL: import.meta.env.VITE_GATEWAY_URL || 'http://host.minikube.internal:3000',
    headers: { 'Content-Type': 'application/json' },
});

export const register = (data) => authApi.post('/register', data);
export const login = (email, password) =>
    authApi.post('/login', {}, { auth: { username: email, password } });
export const oauthLogin = (provider) => {
    window.location.href = `${authApi.defaults.baseURL}/${provider}/login`;
};

export default authApi;
