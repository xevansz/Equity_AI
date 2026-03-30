import axios from 'axios'

const apiClient = axios.create({
  baseURL: '/api',
})

apiClient.interceptors.request.use((config) => {
  const token =
    localStorage.getItem('token') || localStorage.getItem('access_token')
  if (token) {
    config.headers.Authorization = `Bearer ${token}`
  }
  return config
})

apiClient.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response?.status === 401) {
      localStorage.removeItem('token')
      localStorage.removeItem('access_token')
      localStorage.removeItem('eq_search_cache')
      window.location.href = '/login'
    }
    return Promise.reject(error)
  }
)

export default apiClient
