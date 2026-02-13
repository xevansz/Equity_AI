// src/components/AnalysisPanel.jsx
import React, { useState } from 'react'
import FinancialCharts from './FinancialCharts'

const buildChartData = (financial) => {
  const reports = financial?.financials?.income_statement?.annualReports

  if (!Array.isArray(reports)) return []

  return reports
    .slice(0, 5)
    .reverse()
    .map((r) => ({
      year: r.fiscalDateEnding?.slice(0, 4),
      revenue: Number(r.totalRevenue),
      profit: Number(r.operatingIncome || r.grossProfit),
    }))
}

const AnalysisPanel = ({ data }) => {
  const [tab, setTab] = useState('thesis')

  if (!data) {
    return (
      <div className="bg-surface rounded-lg">
        <p className="text-muted text-sm">Search a stock to view analysis</p>
      </div>
    )
  }

  const chartData = buildChartData(data.financial)

  return (
    <div className="p-6 bg-surface rounded-lg">
      <h2 className="text-lg font-semibold mb-3 text-text">Analysis</h2>
      <p className="text-xs text-muted mb-4">
        Query: {data.query} | Symbol: {data.symbol}
      </p>

      {/* Tabs */}
      <div className="flex gap-2 mb-4">
        {['thesis', 'data', 'risk'].map((t) => (
          <button
            key={t}
            onClick={() => setTab(t)}
            className={`px-3 py-1 rounded text-sm ${
              tab === t ? 'bg-primary text-background' : 'bg-background text-muted'
            }`}
          >
            {t === 'thesis' && '💡 Thesis'}
            {t === 'data' && '📊 Data'}
            {t === 'risk' && '⚠️ Risk'}
          </button>
        ))}
      </div>

      {/* SIDE-BY-SIDE LAYOUT */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-4">
        {/* LEFT → RAW API RESPONSE */}
        <div className="bg-background rounded p-3 text-xs overflow-y-auto overflow-x-hidden max-h-[420px] border border-text-muted/10">
          <div className="text-muted mb-2">Raw API Response</div>
          <pre className="whitespace-pre-wrap max-w-full overflow-x-auto text-text">{JSON.stringify(data, null, 2)}</pre>
        </div>

        {/* RIGHT → TAB CONTENT */}
        <div className="text-sm text-text">
          {tab === 'thesis' && (
            <div className="whitespace-pre-line leading-relaxed">
              {data.chat?.answer || 'No thesis available'}
            </div>
          )}

          {tab === 'data' && (
            <>
              {chartData.length > 0 ? (
                <FinancialCharts chartData={chartData} />
              ) : (
                <p className="text-muted">No financial data available</p>
              )}
            </>
          )}

          {tab === 'risk' && (
            <p className="text-muted leading-relaxed">
              {data.research?.risk || 'Risk analysis not available'}
            </p>
          )}
        </div>
      </div>
    </div>
  )
}

export default AnalysisPanel
