import apiClient from './axios'

/* Login API */
export async function login(email, password) {
  const resp = await apiClient.post('/auth/login', { email, password })
  return resp.data
}

/* Register API */
export async function register(email, password) {
  const resp = await apiClient.post('/auth/register', { email, password })
  return resp.data
}

/* Get current user (from Authorization header) */
export async function me() {
  const resp = await apiClient.get('/auth/me')
  return resp.data
}

export default { login, register, me }
