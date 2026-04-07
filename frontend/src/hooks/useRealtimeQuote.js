import { useEffect, useState, useCallback } from 'react'
import { streamClient } from '../websocket/streamClient'

/**
 * Hook to subscribe to real-time quote updates for a symbol
 *
 * @param {string} symbol - Stock symbol to subscribe to
 * @param {string} market - Market (US or INDIA)
 * @returns {object} - { quote, loading, error, connected }
 */
export const useRealtimeQuote = (symbol, market = 'US') => {
  const [quote, setQuote] = useState(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState(null)
  const [connected, setConnected] = useState(false)

  const handleQuote = useCallback(
    (data) => {
      if (data.symbol === symbol) {
        setQuote(data.data)
        setLoading(false)
      }
    },
    [symbol]
  )

  const handleStatus = useCallback((data) => {
    setConnected(data.status === 'connected')
  }, [])

  const handleError = useCallback(
    (data) => {
      if (data.symbol === symbol) {
        setError(data.message)
        setLoading(false)
      }
    },
    [symbol]
  )

  useEffect(() => {
    if (!symbol) return

    // Connect to WebSocket
    streamClient.connect()

    // Subscribe to events
    const unsubQuote = streamClient.on('quote', handleQuote)
    const unsubStatus = streamClient.on('status', handleStatus)
    const unsubError = streamClient.on('error', handleError)

    // Subscribe to symbol
    streamClient.subscribe([symbol], market)

    return () => {
      // Unsubscribe from symbol
      streamClient.unsubscribe([symbol])

      // Remove event listeners
      unsubQuote()
      unsubStatus()
      unsubError()
    }
  }, [symbol, market, handleQuote, handleStatus, handleError])

  return { quote, loading, error, connected }
}
