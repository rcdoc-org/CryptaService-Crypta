import axios from 'axios';
import { ACCESS_TOKEN } from '../../constants';

const api = axios.create({
    // Use the API gateway URL from the environment when provided. Default to
    // localhost so the frontend works during local development without
    // Kubernetes/minikube.
    baseURL:
        import.meta.env.VITE_GATEWAY_URL ||
        'http://localhost:3000',
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
