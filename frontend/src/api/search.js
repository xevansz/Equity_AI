import axios from 'axios'

export async function searchAPI(query, symbol = null) {
  const payload = { query }
  if (symbol) payload.symbol = symbol

  const resp = await axios.post('/api/search', payload)
  return resp.data
}
