import apiClient from './axios'

export async function getNews(symbol) {
  try {
    const resp = await apiClient.get(`/news/${symbol}`)
    return resp.data
  } catch (err) {
    const message =
      err.response?.data?.detail || err.message || 'Request failed'
    throw new Error(message)
  }
}

export default { getNews }
