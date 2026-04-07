import { useEffect, useState, useCallback } from 'react'
import { streamClient } from '../websocket/streamClient'

/**
 * Hook to subscribe to real-time quotes for multiple symbols (watchlist)
 *
 * @param {Array<string>} symbols - Array of stock symbols
 * @param {string} market - Market (US or INDIA)
 * @returns {object} - { quotes, loading, error, connected }
 */
export const useRealtimeWatchlist = (symbols = [], market = 'US') => {
  const [quotes, setQuotes] = useState({})
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState(null)
  const [connected, setConnected] = useState(false)

  const handleQuote = useCallback((data) => {
    setQuotes((prev) => ({
      ...prev,
      [data.symbol]: data.data,
    }))
    setLoading(false)
  }, [])

  const handleStatus = useCallback((data) => {
    setConnected(data.status === 'connected')
    if (data.status === 'connected') {
      setLoading(false)
    }
  }, [])

  const handleError = useCallback((data) => {
    setError(data.message)
    setLoading(false)
  }, [])

  useEffect(() => {
    if (!symbols || symbols.length === 0) {
      setLoading(false)
      return
    }

    // Connect to WebSocket
    streamClient.connect()

    // Subscribe to events
    const unsubQuote = streamClient.on('quote', handleQuote)
    const unsubStatus = streamClient.on('status', handleStatus)
    const unsubError = streamClient.on('error', handleError)

    // Subscribe to all symbols
    streamClient.subscribe(symbols, market)

    return () => {
      // Unsubscribe from symbols
      streamClient.unsubscribe(symbols)

      // Remove event listeners
      unsubQuote()
      unsubStatus()
      unsubError()
    }
  }, [symbols.join(','), market, handleQuote, handleStatus, handleError])

  return { quotes, loading, error, connected }
}
