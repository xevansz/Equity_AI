import apiClient from './axios'

export async function dashboardSearchAPI(query) {
  const payload = { query }
  const resp = await apiClient.post('/dashboard/search', payload)
  return resp.data
}
