import apiClient from './axios'

export const fetchConversations = async () => {
  const res = await apiClient.get('/conversations')
  return res.data
}

export const fetchConversationHistory = async (sessionId) => {
  const res = await apiClient.get(`/conversations/${sessionId}`)
  return res.data
}
