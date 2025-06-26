import axios from 'axios';

// Derive the gateway URL dynamically so the frontend works whether it is served
// locally or from another host.  An environment variable can still override
// this when needed.
const gatewayUrl =
    import.meta.env.VITE_GATEWAY_URL ||
    'http://localhost:3000';

const authApi = axios.create({
    baseURL: gatewayUrl,
    headers: { 'Content-Type': 'application/json' },
});

export const register = (data) => authApi.post('users/register/', data);
export const login = (data) => authApi.post('users/login/', data);

export default authApi;
