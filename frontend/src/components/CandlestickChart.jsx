import React from 'react'
import {
  LineChart,
  Line,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  ResponsiveContainer,
} from 'recharts'

const CandlestickChart = ({ stockData }) => {
  if (!stockData || !stockData['Time Series (Daily)']) {
    return (
      <div className="bg-surface rounded-lg p-6">
        <p className="text-muted">No stock data available</p>
      </div>
    )
  }

  const timeSeries = stockData['Time Series (Daily)']
  const chartData = Object.entries(timeSeries)
    .slice(0, 90)
    .reverse()
    .map(([date, values]) => ({
      date: date,
      close: parseFloat(values['4. close']),
      high: parseFloat(values['2. high']),
      low: parseFloat(values['3. low']),
      open: parseFloat(values['1. open']),
    }))

  return (
    <div className="bg-surface rounded-lg p-6">
      <h3 className="text-lg font-semibold mb-4">
        Stock Price Chart (90 Days)
      </h3>
      <ResponsiveContainer width="100%" height={400}>
        <LineChart data={chartData}>
          <CartesianGrid strokeDasharray="3 3" stroke="#374151" />
          <XAxis
            dataKey="date"
            stroke="#9CA3AF"
            tick={{ fontSize: 12 }}
            tickFormatter={(value) => {
              const d = new Date(value)
              return `${d.getMonth() + 1}/${d.getDate()}`
            }}
          />
          <YAxis
            stroke="#9CA3AF"
            tick={{ fontSize: 12 }}
            domain={['auto', 'auto']}
          />
          <Tooltip
            contentStyle={{
              backgroundColor: '#1F2937',
              border: '1px solid #374151',
              borderRadius: '8px',
            }}
            labelStyle={{ color: '#F3F4F6' }}
            itemStyle={{ color: '#60A5FA' }}
          />
          <Line
            type="monotone"
            dataKey="close"
            stroke="#60A5FA"
            strokeWidth={2}
            dot={false}
          />
        </LineChart>
      </ResponsiveContainer>
    </div>
  )
}

export default CandlestickChart
