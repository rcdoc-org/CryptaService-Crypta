import axios from 'axios';
import { ACCESS_TOKEN } from '../../constants';

// Determine the gateway URL from the current host, falling back to an
// environment variable if provided.  This keeps API calls working when the UI
// is accessed via a remote IP.
const gatewayUrl =
    import.meta.env.VITE_GATEWAY_URL ||
    'http://localhost:3000';

const apiClient = axios.create({
    baseURL: gatewayUrl,
    headers: { 'Content-Type': 'application/json' },
});

apiClient.interceptors.request.use((config) =>{
    const token = localStorage.getItem(ACCESS_TOKEN);
    if (token) {
        config.headers['Authorization'] = `Bearer ${token}`;
    }
    return config
});

// export const fetchFilterTree = (base, params = {}) =>
//     apiClient.get('/filter_tree/', {params: { base, ...params} });
export const fetchFilterTree = (base, params = {}) => {
    const q = { base, ...params };
    if (q.filters !== undefined) {
        q.filters = JSON.stringify(q.filters);
    }
    return apiClient.get('/filter_tree/', { params: q });
};
// export const fetchFilterResults = (base, filters, params = {}) =>
//     apiClient.get('/filter_results/', { params: { base, filters, ...params} });
export const fetchFilterResults = (base, params = {}) => {
    const q = { base, ...params };
    if (q.filters !== undefined) {
        q.filters = JSON.stringify(q.filters);
    }
    return apiClient.get('/filter_results/', { params: q });
};
export const fetchEmailCountPreview = (payload) =>
    apiClient.post('/email-count-preview/', payload);
export const uploadTempFile = (file) => {
    const fd = new FormData();
    fd.append('attachment', file);
    return apiClient.post('/upload-tmp/', fd, {
        headers: { 'Content-Type': 'multipart/form-data' },
    });
};

export const sendEmailRequest = (formData) =>
    apiClient.post('/send-email/', formData, {
        headers: { 'Content-Type': 'multipart/form-data' },
    });
export const fetchSearchResults = (query) => apiClient.get('/search/', { params: { q: query } });
export const fetchDetails = (base, id) => apiClient.get(`/details/${base}/${id}/`);

export default apiClient;
