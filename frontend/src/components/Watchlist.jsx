import React from 'react'
import { useWatchlist } from '../context/WatchlistContext'
import { useRealtimeWatchlist } from '../hooks/useRealtimeWatchlist'
import { Skeleton } from './Skeleton'

const inferMarket = (symbol) => (/\.(NS|BO)$/i.test(symbol) ? 'INDIA' : 'US')

const Watchlist = () => {
  const { items, remove } = useWatchlist()

  const usSymbols = items
    .map((i) => i.symbol)
    .filter((s) => inferMarket(s) === 'US')
  const indiaSymbols = items
    .map((i) => i.symbol)
    .filter((s) => inferMarket(s) === 'INDIA')

  // Real-time price updates via WebSocket — separate subscriptions per market
  const {
    quotes: usQuotes,
    loading: usLoading,
    connected: usConnected,
  } = useRealtimeWatchlist(usSymbols, 'US')
  const {
    quotes: indiaQuotes,
    loading: indiaLoading,
    connected: indiaConnected,
  } = useRealtimeWatchlist(indiaSymbols, 'INDIA')

  const quotes = { ...usQuotes, ...indiaQuotes }
  const loading = usLoading && indiaLoading

  if (items.length === 0) {
    return (
      <div className="p-6 bg-surface rounded-lg">
        <p className="text-muted">No items in your watchlist yet.</p>
      </div>
    )
  }

  return (
    <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-3">
      {items.map((item) => {
        const quote = quotes[item.symbol]
        const isPositive = quote?.change > 0
        const isNegative = quote?.change < 0
        const itemMarket = inferMarket(item.symbol)
        const isItemConnected =
          itemMarket === 'INDIA' ? indiaConnected : usConnected

        return (
          <div
            key={item.symbol}
            className="p-5 bg-surface rounded-xl shadow-sm flex flex-col justify-between hover:shadow-md transition-shadow"
          >
            <div>
              <div className="flex items-center gap-2 mb-1">
                <h2 className="text-lg font-semibold">{item.symbol}</h2>
                {isItemConnected && quote && (
                  <span className="flex items-center gap-1 px-2 py-0.5 bg-green-500/10 text-green-600 dark:text-green-400 rounded text-xs font-medium">
                    <span className="w-1.5 h-1.5 bg-green-500 rounded-full animate-pulse"></span>
                    Live
                  </span>
                )}
                <span className="px-2 py-0.5 bg-primary/10 text-primary rounded text-xs font-medium">
                  {itemMarket}
                </span>
              </div>
              <p className="text-sm text-muted mb-3">{item.name}</p>

              {loading && !quote ? (
                <div className="space-y-2">
                  <Skeleton className="h-7 w-28" />
                  <Skeleton className="h-4 w-20" />
                </div>
              ) : quote ? (
                <div>
                  <p className="text-2xl font-bold mb-1">
                    ${quote.price?.toFixed(2) || '-'}
                  </p>
                  <div className="flex items-center gap-2 text-sm">
                    <span
                      className={`font-medium ${
                        isPositive
                          ? 'text-green-600 dark:text-green-400'
                          : isNegative
                            ? 'text-red-600 dark:text-red-400'
                            : 'text-muted'
                      }`}
                    >
                      {isPositive ? '+' : ''}
                      {quote.change?.toFixed(2) || '0.00'}
                    </span>
                    <span
                      className={`font-medium ${
                        isPositive
                          ? 'text-green-600 dark:text-green-400'
                          : isNegative
                            ? 'text-red-600 dark:text-red-400'
                            : 'text-muted'
                      }`}
                    >
                      ({isPositive ? '+' : ''}
                      {quote.change_percent?.toFixed(2) || '0.00'}%)
                    </span>
                  </div>
                  {quote.timestamp && (
                    <p className="text-xs text-muted mt-1">
                      Updated: {new Date(quote.timestamp).toLocaleTimeString()}
                    </p>
                  )}
                </div>
              ) : (
                <p className="text-xl font-bold text-muted">-</p>
              )}
            </div>

            <button
              onClick={() => remove(item.symbol)}
              className="mt-4 text-sm text-red-500 hover:underline"
            >
              Remove
            </button>
          </div>
        )
      })}

      {/* Market Connection Status Footer */}
      {(usSymbols.length > 0 || indiaSymbols.length > 0) && (
        <div className="sm:col-span-2 lg:col-span-3 mt-2 flex flex-wrap items-center gap-3 text-xs text-muted">
          {usSymbols.length > 0 && (
            <div className="flex items-center gap-1.5">
              <span
                className={`w-2 h-2 rounded-full ${usConnected ? 'bg-green-500 animate-pulse' : 'bg-gray-400'}`}
              />
              <span>
                US Market {usConnected ? 'Connected' : 'Disconnected'}
              </span>
            </div>
          )}
          {indiaSymbols.length > 0 && (
            <div className="flex items-center gap-1.5">
              <span
                className={`w-2 h-2 rounded-full ${indiaConnected ? 'bg-green-500 animate-pulse' : 'bg-gray-400'}`}
              />
              <span>
                India Market {indiaConnected ? 'Connected' : 'Disconnected'}
              </span>
            </div>
          )}
        </div>
      )}
    </div>
  )
}

export default Watchlist
