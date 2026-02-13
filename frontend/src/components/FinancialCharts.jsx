import React from 'react'
import {
  LineChart,
  Line,
  XAxis,
  YAxis,
  Tooltip,
  ResponsiveContainer,
  CartesianGrid,
} from 'recharts'

const formatNumber = (value) => {
  if (value >= 1_000_000_000) return `${(value / 1e9).toFixed(1)}B`
  if (value >= 1_000_000) return `${(value / 1e6).toFixed(1)}M`
  return value
}

const FinancialCharts = ({ chartData }) => {
  if (!chartData || chartData.length === 0) {
    return <p className="text-textMuted text-sm">No financial data available</p>
  }

  return (
    <div className="h-72 w-full">
      <h3 className="text-sm font-semibold mb-2">Revenue & Profit (Last 5 Years)</h3>

      <ResponsiveContainer width="100%" height="100%">
        <LineChart
          data={chartData}
          margin={{ top: 10, right: 20, left: 40, bottom: 10 }} // ✅ KEY FIX
        >
          <CartesianGrid strokeDasharray="3 3" opacity={0.2} />
          <XAxis dataKey="year" />
          <YAxis tickFormatter={formatNumber} />
          <Tooltip formatter={formatNumber} />
          <Line dataKey="revenue" stroke="#38E8D8" strokeWidth={2} />
          <Line dataKey="profit" stroke="#4ADE80" strokeWidth={2} />
        </LineChart>
      </ResponsiveContainer>
    </div>
  )
}

export default FinancialCharts
