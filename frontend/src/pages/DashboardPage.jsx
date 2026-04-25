import React, { useEffect, useState } from 'react'
import SearchBar from '../components/SearchBar'
import LiveAreaChart from '../components/LiveAreaChart'
import MarketMetricsCards from '../components/MarketMetricsCards'
import NewsPanel from '../components/NewsPanel'
import { DashboardSkeleton } from '../components/Skeleton'
import { useSearch } from '../context/SearchContext'
import { useWatchlist } from '../context/WatchlistContext'
import { useRealtimeQuote } from '../hooks/useRealtimeQuote'

const DashboardPage = () => {
  const { items, add } = useWatchlist()
  const {
    data,
    loading,
    error,
    query,
    setQuery,
    market,
    setMarket,
    runSearch,
  } = useSearch()
  const [currentSymbol, setCurrentSymbol] = useState(null)

  // Re-run search when market changes (if there's a query)
  useEffect(() => {
    if (query.trim()) {
      runSearch(query, market)
    }
  }, [market])

  // Real-time quote updates via WebSocket
  const { quote: realtimeQuote, connected } = useRealtimeQuote(
    currentSymbol,
    data?.market_snapshot?.market || 'US'
  )

  // Update current symbol when search data changes
  useEffect(() => {
    if (data?.symbol) {
      setCurrentSymbol(data.symbol)
    }
  }, [data?.symbol])

  const isInWatchlist =
    !!data?.company_name &&
    items.some(
      (item) =>
        item.company_name?.toLowerCase().trim() ===
        data.company_name.toLowerCase().trim()
    )
  const companyNotFound = data?.search_status === 'company_not_found'
  const noStockData = data?.search_status === 'no_stock_data'

  // Merge real-time quote with market snapshot
  const marketSnapshot = data?.market_snapshot
    ? {
        ...data.market_snapshot,
        ...(realtimeQuote && {
          price: realtimeQuote.price,
          change: realtimeQuote.change,
          change_percent: realtimeQuote.change_percent,
          volume: realtimeQuote.volume,
          high: realtimeQuote.high,
          low: realtimeQuote.low,
          open: realtimeQuote.open,
          prev_close: realtimeQuote.prev_close,
          timestamp: realtimeQuote.timestamp,
        }),
      }
    : null

  return (
    <div className="bg-background w-full">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        {/* Header */}
        <div className="mb-4">
          <h1 className="text-3xl font-bold mb-2">Research Dashboard</h1>
          <p className="text-muted">Analyze stocks with AI-powered insights</p>
        </div>

        <SearchBar
          query={query}
          setQuery={setQuery}
          onSearch={runSearch}
          market={market}
          setMarket={setMarket}
        />

        {loading && <DashboardSkeleton />}

        {error && (
          <div className="mt-8 p-4 bg-error/10 border border-error/20 rounded-lg">
            <p className="text-error">Error: {error} </p>
          </div>
        )}

        {!loading && data && (
          <div className="mt-5 space-y-6">
            {companyNotFound ? (
              <div className="p-6 bg-error/10 border border-error/20 rounded-lg">
                <h3 className="text-lg font-semibold text-error mb-2">
                  No Company Found
                </h3>
                <p className="text-muted">
                  Could not find a company matching `&quot;`{data.query}
                  `&quot;`. Please try a different search term or stock symbol.
                </p>
              </div>
            ) : (
              <>
                <div className="flex items-center justify-between">
                  <div>
                    <div className="flex items-center gap-3">
                      <h2 className="text-2xl font-bold">{data.symbol}</h2>
                      {connected && (
                        <span className="flex items-center gap-1 px-2 py-1 bg-green-500/10 text-green-600 dark:text-green-400 rounded text-xs font-medium">
                          <span className="w-2 h-2 bg-green-500 rounded-full animate-pulse"></span>
                          Live
                        </span>
                      )}
                    </div>
                    <p className="text-sm text-muted">Search: {data.query}</p>
                  </div>
                  <button
                    onClick={() =>
                      add(data.symbol, data.company_name, data.company_name)
                    }
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

                {noStockData && (
                  <div className="p-4 bg-yellow-500/10 border border-yellow-500/20 rounded-lg">
                    <p className="text-yellow-600 dark:text-yellow-400">
                      No stock data available. This may be due to API rate
                      limits or the symbol may not have recent trading data.
                    </p>
                  </div>
                )}

                <LiveAreaChart
                  symbol={data.symbol}
                  market={market}
                  chartData={
                    data.intraday_data ||
                    data.stock_data?.['Time Series (Daily)']
                  }
                  prevClose={
                    marketSnapshot?.prev_close ||
                    marketSnapshot?.price - marketSnapshot?.change
                  }
                />
                <MarketMetricsCards marketSnapshot={marketSnapshot} />
                <NewsPanel newsData={data.news} />
              </>
            )}
          </div>
        )}
      </div>
    </div>
  )
}

export default DashboardPage
