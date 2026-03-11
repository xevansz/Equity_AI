// src/pages/DashboardPage.jsx
import React from 'react'
import SearchBar from '../components/SearchBar'
import AnalysisPanel from '../components/AnalysisPanel'
import { useSearch } from '../context/SearchContext'
import { useWatchlist } from '../context/WatchlistContext'

const DashboardPage = () => {
  const { items, add } = useWatchlist()
  const { data, loading, error, query, setQuery, runSearch } = useSearch()
  const isInWatchlist =
    !!data?.symbol && items.some((item) => item.symbol === data.symbol)

  return (
    <div className="bg-background w-full">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        {/* Header */}
        <div className="mb-8">
          <h1 className="text-3xl font-bold mb-2">Research Dashboard</h1>
          <p className="text-muted">Analyze stocks with AI-powered insights</p>
        </div>

        <SearchBar query={query} setQuery={setQuery} onSearch={runSearch} />

        {loading && (
          <div className="mt-8 p-8 bg-surface rounded-lg text-center">
            <div className="inline-block animate-spin rounded-full h-8 w-8 border-b-2 border-primary"></div>
            <p className="mt-4 text-muted">Analyzing...</p>
          </div>
        )}

        {error && (
          <div className="mt-8 p-4 bg-error/10 border border-error/20 rounded-lg">
            <p className="text-error">Error: {error} </p>
          </div>
        )}

        {!loading && data && (
          <div className="mt-8 space-y-4">
            <div>
              <button
                onClick={() => add(data.symbol, data.query || data.symbol)}
                disabled={isInWatchlist}
                className={`px-4 py-2 rounded-lg transition ${
                  isInWatchlist
                    ? 'bg-green-600 text-white cursor-not-allowed'
                    : 'bg-primary text-white hover:opacity-90'
                }`}
              >
                {isInWatchlist ? '✓ Added' : '+ Add to Watchlist'}
              </button>
            </div>

            <AnalysisPanel data={data} />
          </div>
        )}
      </div>
    </div>
  )
}

export default DashboardPage
