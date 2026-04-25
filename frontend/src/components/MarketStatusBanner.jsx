import React from 'react'
import { useMarketStatus } from '../hooks/useMarketStatus'

const STATUS_STYLES = {
  open: {
    bar: 'bg-green-500/10 border-green-500/20 text-green-700 dark:text-green-400',
    dot: 'bg-green-500 animate-pulse',
    label: 'Open',
  },
  pre_market: {
    bar: 'bg-yellow-500/10 border-yellow-500/20 text-yellow-700 dark:text-yellow-400',
    dot: 'bg-yellow-500',
    label: 'Pre-Market',
  },
  after_hours: {
    bar: 'bg-orange-500/10 border-orange-500/20 text-orange-700 dark:text-orange-400',
    dot: 'bg-orange-500',
    label: 'After Hours',
  },
  weekend: {
    bar: 'bg-gray-500/10 border-gray-500/20 text-gray-500 dark:text-gray-400',
    dot: 'bg-gray-400',
    label: 'Closed',
  },
  closed: {
    bar: 'bg-gray-500/10 border-gray-500/20 text-gray-500 dark:text-gray-400',
    dot: 'bg-gray-400',
    label: 'Closed',
  },
  unknown: {
    bar: 'bg-gray-500/10 border-gray-500/20 text-gray-500 dark:text-gray-400',
    dot: 'bg-gray-400',
    label: 'Unknown',
  },
}

const MarketPill = ({ market }) => {
  const { status, marketLabel, hoursLabel, nextOpenTime } =
    useMarketStatus(market)
  const styles = STATUS_STYLES[status] || STATUS_STYLES.unknown

  const nextOpenLabel = nextOpenTime
    ? new Date(nextOpenTime).toLocaleString(undefined, {
        weekday: 'short',
        month: 'short',
        day: 'numeric',
        hour: '2-digit',
        minute: '2-digit',
      })
    : null

  return (
    <div
      className={`flex items-center gap-2 px-3 py-1.5 rounded-lg border text-xs font-medium ${styles.bar}`}
    >
      <span className={`w-2 h-2 rounded-full flex-shrink-0 ${styles.dot}`} />
      <span className="font-semibold">{marketLabel}</span>
      <span className="opacity-70">·</span>
      <span>{styles.label}</span>
      {hoursLabel && (
        <span className="opacity-60 hidden sm:inline">({hoursLabel})</span>
      )}
      {!status.includes('open') && nextOpenLabel && (
        <span className="opacity-60 hidden md:inline">
          · Opens {nextOpenLabel}
        </span>
      )}
    </div>
  )
}

const MarketStatusBanner = ({ markets = ['US', 'INDIA'] }) => {
  return (
    <div className="flex flex-wrap items-center gap-2 mb-4">
      {markets.map((m) => (
        <MarketPill key={m} market={m} />
      ))}
    </div>
  )
}

export default MarketStatusBanner
