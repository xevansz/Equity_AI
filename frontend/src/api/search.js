import apiClient from './axios'

export async function searchAPI(query, symbol = null) {
  const payload = { query }
  if (symbol) payload.symbol = symbol

  const resp = await apiClient.post('/search', payload)
  return resp.data
}
