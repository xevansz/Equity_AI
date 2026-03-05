import apiClient from './axios'

export async function getFinancialData(symbol) {
  try {
    const resp = await apiClient.post('/financial', { symbol })
    return resp.data
  } catch (err) {
    const message =
      err.response?.data?.detail || err.message || 'Request failed'
    throw new Error(message)
  }
}

export default { getFinancialData }
