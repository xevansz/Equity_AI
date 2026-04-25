import apiClient from './axios'

export async function dashboardSearchAPI(query, market = 'US') {
  const payload = { query, market }
  const resp = await apiClient.post('/dashboard/search', payload)
  return resp.data
}
