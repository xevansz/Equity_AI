import React, { useEffect, useRef } from 'react'
import { createChart, CandlestickSeries } from 'lightweight-charts'

const CandlestickChart = ({ stockData }) => {
  const chartContainerRef = useRef(null)
  const chartRef = useRef(null)
  const candlestickSeriesRef = useRef(null)

  useEffect(() => {
    if (!chartContainerRef.current) return

    // Create chart instance
    const chart = createChart(chartContainerRef.current, {
      layout: {
        background: { color: '#1F2937' },
        textColor: '#9CA3AF',
      },
      grid: {
        vertLines: { color: '#374151' },
        horzLines: { color: '#374151' },
      },
      width: chartContainerRef.current.clientWidth,
      height: 500,
      timeScale: {
        timeVisible: true,
        secondsVisible: false,
      },
    })

    // Add candlestick series
    const candlestickSeries = chart.addSeries(CandlestickSeries, {
      upColor: '#10B981',
      downColor: '#EF4444',
      borderVisible: false,
      wickUpColor: '#10B981',
      wickDownColor: '#EF4444',
    })

    chartRef.current = chart
    candlestickSeriesRef.current = candlestickSeries

    // Handle resize
    const handleResize = () => {
      if (chartContainerRef.current) {
        chart.applyOptions({
          width: chartContainerRef.current.clientWidth,
        })
      }
    }

    window.addEventListener('resize', handleResize)

    return () => {
      window.removeEventListener('resize', handleResize)
      chart.remove()
    }
  }, [stockData])

  useEffect(() => {
    if (
      !candlestickSeriesRef.current ||
      !stockData ||
      !stockData['Time Series (Daily)']
    ) {
      return
    }

    const timeSeries = stockData['Time Series (Daily)']

    // Transform data to lightweight-charts format
    const candleData = Object.entries(timeSeries)
      .map(([date, values]) => ({
        time: date, // YYYY-MM-DD format
        open: parseFloat(values['1. open']),
        high: parseFloat(values['2. high']),
        low: parseFloat(values['3. low']),
        close: parseFloat(values['4. close']),
      }))
      .sort((a, b) => new Date(a.time) - new Date(b.time)) // Sort chronologically

    candlestickSeriesRef.current.setData(candleData)

    // Fit content to visible range
    if (chartRef.current) {
      chartRef.current.timeScale().fitContent()
    }
  }, [stockData])

  if (!stockData || !stockData['Time Series (Daily)']) {
    return null
  }

  return (
    <div className="bg-surface rounded-lg p-6 pt-4">
      <h3 className="text-lg font-semibold mb-3">
        Stock Price Chart (Candlestick)
      </h3>
      <div ref={chartContainerRef} />
    </div>
  )
}

export default CandlestickChart
