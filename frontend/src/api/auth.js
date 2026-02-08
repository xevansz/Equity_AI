import axios from 'axios';

/**
 * Login API
 */
export async function login(email, password) {
	const resp = await axios.post('/api/auth/login', { email, password });
	return resp.data;
}

/**
 * Register API
 */
export async function register(email, password) {
	const resp = await axios.post('/api/auth/register', { email, password });
	return resp.data;
}

/**
 * Get current user (from Authorization header)
 * Relies on axios.defaults.headers.common['Authorization']
 */
export async function me() {
	const resp = await axios.get('/api/auth/me');
	return resp.data;
}

export default { login, register, me };
