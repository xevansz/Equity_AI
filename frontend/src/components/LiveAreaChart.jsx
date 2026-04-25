import React, { useEffect, useMemo, useRef, useState } from 'react'
import {
  Area,
  AreaChart,
  ResponsiveContainer,
  Tooltip,
  XAxis,
  YAxis,
} from 'recharts'
import { streamClient } from '../websocket/streamClient'
import {
  useMarketStatus,
  getMarketStatusDisplay,
} from '../hooks/useMarketStatus'
import { smoothPriceData } from '../utils/cubicSpline'

/**
 * LiveAreaChart - Groww-style area chart with real-time updates
 *
 * Features:
 * - Cubic spline smoothed 1-minute candles
 * - Green/red gradient based on previous close
 * - Real-time WebSocket updates
 * - Market hours aware (pauses when closed)
 */

const LiveAreaChart = ({ symbol, market, chartData, prevClose = 0 }) => {
  const [data, setData] = useState([])
  const [loading, setLoading] = useState(true)
  const [liveTick, setLiveTick] = useState(null)
  const chartDataRef = useRef(chartData)
  const symbolRef = useRef(symbol)

  // Track refs for latest values in callbacks
  useEffect(() => {
    chartDataRef.current = chartData
    symbolRef.current = symbol
  }, [chartData, symbol])

  // Market status
  const { isOpen, status, hoursLabel } = useMarketStatus(market)
  const statusDisplay = getMarketStatusDisplay(status)

  // Initialize chart data from props
  useEffect(() => {
    if (!chartData || chartData.length === 0) {
      setData([])
      setLoading(false)
      return
    }

    // Transform and sort data
    const transformed = chartData
      .map((item) => ({
        timestamp: item.timestamp || item.datetime,
        open: Number(item.open) || 0,
        high: Number(item.high) || 0,
        low: Number(item.low) || 0,
        close: Number(item.close) || 0,
        volume: Number(item.volume) || 0,
      }))
      .sort((a, b) => new Date(a.timestamp) - new Date(b.timestamp))

    // Apply cubic spline smoothing
    const smoothed = smoothPriceData(transformed, 3)

    setData(smoothed)
    setLoading(false)
  }, [chartData])

  // WebSocket for live updates
  useEffect(() => {
    if (!symbol || !isOpen) return

    streamClient.connect()

    const handleQuote = (msg) => {
      if (msg.symbol === symbol && msg.data) {
        setLiveTick({
          price: msg.data.price,
          timestamp: msg.data.timestamp,
          volume: msg.data.volume,
        })
      }
    }

    const unsubQuote = streamClient.on('quote', handleQuote)
    streamClient.subscribe([symbol], market, '1min')

    return () => {
      unsubQuote()
      streamClient.unsubscribe([symbol])
    }
  }, [symbol, market, isOpen])

  // Append live tick to data
  useEffect(() => {
    if (!liveTick || data.length === 0) return

    setData((prev) => {
      const last = prev[prev.length - 1]
      if (!last) return prev

      // Check if we need a new candle or update existing
      const lastTime = new Date(last.timestamp)
      const tickTime = new Date(liveTick.timestamp)
      const minuteDiff = Math.floor((tickTime - lastTime) / 60000)

      if (minuteDiff >= 1) {
        // New minute - create new candle
        const newPoint = {
          timestamp: liveTick.timestamp,
          open: last.close,
          high: liveTick.price,
          low: liveTick.price,
          close: liveTick.price,
          volume: liveTick.volume || 0,
          original: true,
        }

        // Keep only last 100 points and resmooth
        const newData = [...prev.slice(-99), newPoint]
        return smoothPriceData(newData, 3)
      } else {
        // Same minute - update last candle
        const updated = [...prev]
        const lastIndex = updated.length - 1
        const originalPoint = updated[lastIndex]

        updated[lastIndex] = {
          ...originalPoint,
          high: Math.max(originalPoint.high, liveTick.price),
          low: Math.min(originalPoint.low, liveTick.price),
          close: liveTick.price,
          volume: (originalPoint.volume || 0) + (liveTick.volume || 0),
        }

        return updated
      }
    })
  }, [liveTick])

  // Calculate trend for coloring
  const basePrice = useMemo(() => {
    if (prevClose > 0) return prevClose
    if (data.length > 0) return data[0].open
    return 0
  }, [prevClose, data])

  const currentPrice = useMemo(() => {
    if (data.length === 0) return 0
    return data[data.length - 1].close
  }, [data])

  const isUp = currentPrice >= basePrice

  // Chart colors based on trend
  const strokeColor = isUp ? '#10B981' : '#EF4444'
  const gradientId = isUp ? 'greenGradient' : 'redGradient'

  // Format time for X-axis
  const formatTime = (timestamp) => {
    try {
      const date = new Date(timestamp)
      return date.toLocaleTimeString('en-US', {
        hour: '2-digit',
        minute: '2-digit',
        hour12: false,
      })
    } catch {
      return ''
    }
  }

  // Custom tooltip
  const CustomTooltip = ({ active, payload }) => {
    if (!active || !payload || payload.length === 0) return null

    const point = payload[0].payload
    return (
      <div className="bg-surface border border-text-muted/20 rounded-lg p-3 shadow-lg">
        <p className="text-sm text-muted mb-1">
          {new Date(point.timestamp).toLocaleString()}
        </p>
        <div className="space-y-1">
          <p className="text-sm font-semibold">
            Close: ${point.close.toFixed(2)}
          </p>
          <p className="text-xs text-muted">Open: ${point.open.toFixed(2)}</p>
          <p className="text-xs text-muted">High: ${point.high.toFixed(2)}</p>
          <p className="text-xs text-muted">Low: ${point.low.toFixed(2)}</p>
          {point.volume > 0 && (
            <p className="text-xs text-muted">
              Vol: {point.volume.toLocaleString()}
            </p>
          )}
        </div>
      </div>
    )
  }

  if (loading) {
    return (
      <div className="bg-surface rounded-lg p-6 h-96 flex items-center justify-center">
        <div className="animate-pulse text-muted">Loading chart...</div>
      </div>
    )
  }

  if (data.length === 0) {
    return (
      <div className="bg-surface rounded-lg p-6">
        <div className="flex items-center justify-between mb-4">
          <h3 className="text-lg font-semibold">Price Chart</h3>
          <span
            className={`px-2 py-1 rounded text-xs font-medium bg-${statusDisplay.color}-500/10 text-${statusDisplay.color}-600`}
          >
            {statusDisplay.label}
          </span>
        </div>
        <p className="text-muted text-center py-12">
          No intraday data available
        </p>
      </div>
    )
  }

  return (
    <div className="bg-surface rounded-lg p-6">
      <div className="flex items-center justify-between mb-4">
        <div>
          <h3 className="text-lg font-semibold">Price Chart</h3>
          <p className="text-xs text-muted">{hoursLabel} • 1-min intervals</p>
        </div>
        <div className="flex items-center gap-2">
          {statusDisplay.pulse && (
            <span className="flex items-center gap-1 px-2 py-1 bg-green-500/10 text-green-600 rounded text-xs font-medium">
              <span className="w-2 h-2 bg-green-500 rounded-full animate-pulse"></span>
              Live
            </span>
          )}
          {!statusDisplay.pulse && (
            <span
              className={`px-2 py-1 rounded text-xs font-medium bg-${statusDisplay.color}-500/10 text-${statusDisplay.color}-600`}
            >
              {statusDisplay.label}
            </span>
          )}
        </div>
      </div>

      <div className="h-80">
        <ResponsiveContainer width="100%" height="100%">
          <AreaChart
            data={data}
            margin={{ top: 10, right: 10, left: 0, bottom: 0 }}
          >
            <defs>
              <linearGradient id="greenGradient" x1="0" y1="0" x2="0" y2="1">
                <stop offset="5%" stopColor="#10B981" stopOpacity={0.3} />
                <stop offset="95%" stopColor="#10B981" stopOpacity={0} />
              </linearGradient>
              <linearGradient id="redGradient" x1="0" y1="0" x2="0" y2="1">
                <stop offset="5%" stopColor="#EF4444" stopOpacity={0.3} />
                <stop offset="95%" stopColor="#EF4444" stopOpacity={0} />
              </linearGradient>
            </defs>

            <XAxis
              dataKey="timestamp"
              tickFormatter={formatTime}
              tick={{ fontSize: 12, fill: '#6B7280' }}
              axisLine={false}
              tickLine={false}
              minTickGap={30}
            />

            <YAxis
              domain={['auto', 'auto']}
              tick={{ fontSize: 12, fill: '#6B7280' }}
              axisLine={false}
              tickLine={false}
              tickFormatter={(value) => `$${value.toFixed(2)}`}
              width={60}
            />

            <Tooltip content={<CustomTooltip />} />

            <Area
              type="monotone"
              dataKey="close"
              stroke={strokeColor}
              strokeWidth={2}
              fill={`url(#${gradientId})`}
              isAnimationActive={false}
            />
          </AreaChart>
        </ResponsiveContainer>
      </div>

      {/* Price info */}
      <div className="flex items-center justify-between mt-4 pt-4 border-t border-text-muted/10">
        <div className="flex gap-4 text-sm">
          <span className="text-muted">
            Open:{' '}
            <span className="text-text font-medium">
              ${data[0]?.open?.toFixed(2) || '-'}
            </span>
          </span>
          <span className="text-muted">
            High:{' '}
            <span className="text-green-500 font-medium">
              ${Math.max(...data.map((d) => d.high))?.toFixed(2) || '-'}
            </span>
          </span>
          <span className="text-muted">
            Low:{' '}
            <span className="text-red-500 font-medium">
              ${Math.min(...data.map((d) => d.low))?.toFixed(2) || '-'}
            </span>
          </span>
        </div>
        <div
          className={`text-lg font-bold ${isUp ? 'text-green-500' : 'text-red-500'}`}
        >
          ${currentPrice.toFixed(2)}
          <span className="text-sm font-normal text-muted ml-2">
            {(((currentPrice - basePrice) / basePrice) * 100).toFixed(2)}%
          </span>
        </div>
      </div>
    </div>
  )
}

export default LiveAreaChart
