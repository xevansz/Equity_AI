import axios from 'axios'

const BASE_URL = '/api/watchlist'

const getAuthHeaders = () => {
  const token = localStorage.getItem('access_token')

  if (!token) {
    throw new Error('No auth token found')
  }

  return {
    Authorization: `Bearer ${token}`,
    'Content-Type': 'application/json',
  }
}

/**
 * Fetch paginated watchlist
 * @param {number} limit
 * @param {string|null} after ISO datetime string (cursor)
 */
export const fetchWatchlist = async (limit = 20, after = null) => {
  try {
    const headers = getAuthHeaders()

    const response = await axios.get(BASE_URL, {
      headers,
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
    const headers = await getAuthHeaders()

    const response = await axios.post(BASE_URL, { symbol, name }, { headers })

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
    const headers = await getAuthHeaders()

    const response = await axios.delete(`${BASE_URL}/${symbol}`, {
      headers,
    })

    return response.data
  } catch (error) {
    console.error(
      'Error removing from watchlist:',
      error.response?.data || error.message
    )
    throw error
  }
}
