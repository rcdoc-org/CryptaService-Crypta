import axios from 'axios';

// Derive the gateway URL dynamically so the frontend works whether it is served
// locally or from another host.  An environment variable can still override
// this when needed.
const gatewayUrl =
    import.meta.env.VITE_GATEWAY_URL ||
    `${window.location.protocol}//${window.location.hostname}:3000`;

const authApi = axios.create({
    baseURL: gatewayUrl,
    headers: { 'Content-Type': 'application/json' },
});

export const register = (data) => authApi.post('/register', data);
export const login = (email, password) =>
    authApi.post('/login', {}, { auth: { username: email, password } });
export const oauthLogin = (provider) => {
    window.location.href = `${authApi.defaults.baseURL}/${provider}/login`;
};

export default authApi;
