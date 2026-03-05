import React from 'react'
import {
  createContext,
  useContext,
  useEffect,
  useState,
  useCallback,
} from 'react'
import {
  fetchWatchlist as apiFetchWatchlist,
  addToWatchlist,
  removeFromWatchlist,
} from '../api/watchlist'

const WatchlistContext = createContext()

export const WatchlistProvider = ({ children }) => {
  const [items, setItems] = useState([])
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState(null)
  const [cursor, setCursor] = useState(null)
  const [hasMore, setHasMore] = useState(true)

  /**
   * Fetch watchlist (initial or paginated)
   */
  const fetchWatchlist = useCallback(
    async (reset = false) => {
      try {
        setLoading(true)
        setError(null)

        const data = await apiFetchWatchlist(20, reset ? null : cursor)

        if (reset) {
          setItems(data.items)
        } else {
          setItems((prev) => [...prev, ...data.items])
        }

        setCursor(data.next_cursor)
        setHasMore(!!data.next_cursor)
      } catch (err) {
        setError(err.response?.data?.detail || 'Failed to load watchlist')
      } finally {
        setLoading(false)
      }
    },
    [cursor]
  )

  /**
   * Add symbol
   */
  const add = async (symbol, name) => {
    try {
      setError(null)
      await addToWatchlist(symbol, name)

      // Optimistic refresh (simple version)
      await fetchWatchlist(true)
    } catch (err) {
      setError(err.response?.data?.detail || 'Failed to add symbol')
      throw err
    }
  }

  /**
   * Remove symbol
   */
  const remove = async (symbol) => {
    try {
      setError(null)
      await removeFromWatchlist(symbol)

      // Optimistic local update
      setItems((prev) => prev.filter((item) => item.symbol !== symbol))
    } catch (err) {
      setError(err.response?.data?.detail || 'Failed to remove symbol')
      throw err
    }
  }

  /**
   * Auto-fetch on login
   */
  useEffect(() => {
    const token =
      localStorage.getItem('access_token') || localStorage.getItem('token')
    if (token) {
      fetchWatchlist(true)
    }
  }, [])

  return (
    <WatchlistContext.Provider
      value={{
        items,
        loading,
        error,
        hasMore,
        fetchWatchlist,
        add,
        remove,
      }}
    >
      {children}
    </WatchlistContext.Provider>
  )
}

export const useWatchlist = () => {
  const context = useContext(WatchlistContext)
  if (!context) {
    throw new Error('useWatchlist must be used within WatchlistProvider')
  }
  return context
}
