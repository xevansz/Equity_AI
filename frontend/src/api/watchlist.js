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
  } catch (error) {
    console.error(
      'Error fetching watchlist:',
      error.response?.data || error.message
    )
    throw error
  }
}

/**
 * Add symbol to watchlist
 */
export const addToWatchlist = async (symbol, name) => {
  try {
    const response = await apiClient.post(BASE_URL, { symbol, name })

    return response.data
  } catch (error) {
    console.error(
      'Error adding to watchlist:',
      error.response?.data || error.message
    )
    throw error
  }
}

/**
 * Remove symbol from watchlist
 */
export const removeFromWatchlist = async (symbol) => {
  try {
    const response = await apiClient.delete(`${BASE_URL}/${symbol}`)

    return response.data
  } catch (error) {
    console.error(
      'Error removing from watchlist:',
      error.response?.data || error.message
    )
    throw error
  }
}
