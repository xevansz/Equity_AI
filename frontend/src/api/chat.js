import apiClient from './axios'

export async function sendChat(query, sessionId) {
  try {
    const resp = await apiClient.post('/chat', {
      query,
      session_id: sessionId,
    })
    return resp.data
  } catch (err) {
    const message =
      err.response?.data?.detail || err.message || 'Request failed'
    throw new Error(message)
  }
}

export default { sendChat }
