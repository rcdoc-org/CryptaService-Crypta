import axios from 'axios';
import { ACCESS_TOKEN } from '../../constants';

// Compute the gateway URL based on the current page host so the frontend works
// when accessed remotely.  This can be overridden with the VITE_GATEWAY_URL
// environment variable for special cases.
const gatewayUrl =
    import.meta.env.VITE_GATEWAY_URL ||
    `${window.location.protocol}//${window.location.hostname}:3000`;

const api = axios.create({
    baseURL: gatewayUrl,
});

api.interceptors.request.use(
    (config) => {
        const token = localStorage.getItem(ACCESS_TOKEN);
        if (token) {
            config.headers['Authorization'] = `Bearer ${token}`;
        }
        return config;
    },
    (error) => {
        return Promise.reject(error);
    }
);

export default api;
