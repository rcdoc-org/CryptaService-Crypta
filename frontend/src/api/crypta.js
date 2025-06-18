import axios from 'axios';

const apiClient = axios.create({
    baseURL: import.meta.env.VITE_GATEWAY_URL || 'http://host.minikube.internal:3000',
    headers: { 'Content-Type': 'application/json' },
});

export const fetchFilterTree = (base) => apiClient.get(`/filter_results?base=${base}`);
export const fetchEmailCountPreview = (params) => apiClient.get('/email_count_preview', { params });
export const fetchSearchResults = (query) => apiClient.get('/search', { params: { q: query } });
export const fetchDetails = (base, id) => apiClient.get(`/details/${base}/${id}`);

export default apiClient;
