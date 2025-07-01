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

// Login functions
export const register = (data) => authApi.post('/users/register/', data);
export const login = (data) => authApi.post('/users/login/', data);
export const verifyMfa = (data) => authApi.post('/users/verify_mfa/', data);
export const ssoLogin = () => authApi.get('/sso/login/'); // Doesn't allow for redirect with Microsoft required using window.location.href
export const ssoCallback = (parameters) => authApi.get('/sso/callback/', { parameters })
export const AUTH_SSO_LOGIN_URL = gatewayUrl + '/sso/login/'

// User Management functions
export const fetchUsers = () => authApi.get('/users/');
export const fetchRoles = () => authApi.get('/roles/');
export const fetchTokens = () => authApi.get('/tokens/');
export const fetchOrganizations = () => authApi.get('/organizations/');
export const fetchLoginAttempts = () => authApi.get('/login_attempts/');
export const fetchCryptaGroups = () => authApi.get('/crypta_groups/');
export const fetchQueryPermissions = () => authApi.get('/query_permissions/');

export const createUser = (data) => authApi.post('/users/register/', data);
export const deleteUser = (id) => authApi.delete(`/users/${id}/`);

export const createRole = (data) => authApi.post('/roles/create/', data);
export const deleteRole = (id) => authApi.delete(`/roles/${id}/`);

export const createOrganization = (data) => authApi.post('/organizations/create/', data);
export const deleteOrganization = (id) => authApi.delete(`/organizations/${id}/`);

export const createCryptaGroup = (data) => authApi.post('/crypta_groups/create/', data);
export const deleteCryptaGroup = (id) => authApi.delete(`/crypta_groups/${id}/`);

export const createQueryPermission = (data) => authApi.post('/query_permissions/create/', data);
export const deleteQueryPermission = (id) => authApi.delete(`/query_permissions/${id}/`);

export default authApi;
