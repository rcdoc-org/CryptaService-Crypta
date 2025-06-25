import axios from 'axios';

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

export const fetchFilterTree = (base) => apiClient.get(`/filter_results?base=${base}`);
export const fetchEmailCountPreview = (params) => apiClient.get('/email_count_preview', { params });
export const fetchSearchResults = (query) => apiClient.get('/search', { params: { q: query } });
export const fetchDetails = (base, id) => apiClient.get(`/details/${base}/${id}`);

export default apiClient;
