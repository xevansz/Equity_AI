import apiClient from './axios'

const BASE_URL = '/watchlist'

/**
 * Fetch paginated watchlist
 * @param {number} limit
 * @param {string|null} after ISO datetime string (cursor)
 */
export const fetchWatchlist = async (limit = 20, after = null) => {
  try {
    const response = await apiClient.get(BASE_URL, {
      params: {
        limit,
        ...(after && { after }),
      },
    })

    return response.data
  } catch (err) {
    const message =
      err.response?.data?.detail || err.message || 'Request failed'
    throw new Error(message)
  }
}

/**
 * Add symbol to watchlist
 */
export const addToWatchlist = async (symbol, name, company_name) => {
  try {
    const response = await apiClient.post(BASE_URL, {
      symbol,
      name,
      company_name,
    })

    return response.data
  } catch (err) {
    const message =
      err.response?.data?.detail || err.message || 'Request failed'
    throw new Error(message)
  }
}

/**
 * Remove symbol from watchlist
 */
export const removeFromWatchlist = async (symbol) => {
  try {
    const response = await apiClient.delete(`${BASE_URL}/${symbol}`)

    return response.data
  } catch (err) {
    const message =
      err.response?.data?.detail || err.message || 'Request failed'
    throw new Error(message)
  }
}
