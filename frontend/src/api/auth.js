import axios from 'axios';

const authApi = axios.create({
    // Allow overriding the API gateway URL via environment variable. Fall back
    // to localhost when running the services locally so that registration and
    // login work without a Kubernetes setup.
    baseURL:
        import.meta.env.VITE_GATEWAY_URL ||
        'http://localhost:3000',
    headers: { 'Content-Type': 'application/json' },
});

export const register = (data) => authApi.post('/register', data);
export const login = (email, password) =>
    authApi.post('/login', {}, { auth: { username: email, password } });
export const oauthLogin = (provider) => {
    window.location.href = `${authApi.defaults.baseURL}/${provider}/login`;
};

export default authApi;
