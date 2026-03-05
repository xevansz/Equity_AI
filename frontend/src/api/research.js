import apiClient from './axios'

export async function getResearch(symbol) {
  try {
    const resp = await apiClient.post('/research', { symbol })
    return resp.data
  } catch (err) {
    const message =
      err.response?.data?.detail || err.message || 'Request failed'
    throw new Error(message)
  }
}

export default { getResearch }
