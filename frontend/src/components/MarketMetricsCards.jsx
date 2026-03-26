import React from 'react'
import {
  TrendingUp,
  TrendingDown,
  DollarSign,
  Activity,
  BarChart3,
  Calendar,
} from 'lucide-react'

const MarketMetricsCards = ({ marketSnapshot }) => {
  if (!marketSnapshot) {
    return null
  }

  const formatNumber = (num, decimals = 2) => {
    if (num === null || num === undefined) return 'N/A'
    return num.toLocaleString('en-US', {
      minimumFractionDigits: decimals,
      maximumFractionDigits: decimals,
    })
  }

  const formatVolume = (vol) => {
    if (vol === null || vol === undefined) return 'N/A'
    if (vol >= 1_000_000_000) {
      return `${(vol / 1_000_000_000).toFixed(2)}B`
    }
    if (vol >= 1_000_000) {
      return `${(vol / 1_000_000).toFixed(2)}M`
    }
    if (vol >= 1_000) {
      return `${(vol / 1_000).toFixed(2)}K`
    }
    return vol.toLocaleString()
  }

  const isPositive = marketSnapshot.change && marketSnapshot.change > 0
  const isNegative = marketSnapshot.change && marketSnapshot.change < 0

  const metrics = [
    {
      label: 'Price',
      value: `$${formatNumber(marketSnapshot.price)}`,
      icon: <DollarSign className="w-5 h-5" />,
      highlight: true,
    },
    {
      label: 'Change',
      value:
        marketSnapshot.change !== null && marketSnapshot.change !== undefined
          ? `${isPositive ? '+' : ''}$${formatNumber(marketSnapshot.change)}`
          : 'N/A',
      icon: isPositive ? (
        <TrendingUp className="w-5 h-5" />
      ) : (
        <TrendingDown className="w-5 h-5" />
      ),
      color: isPositive ? 'text-green-500' : isNegative ? 'text-red-500' : '',
    },
    {
      label: 'Change %',
      value:
        marketSnapshot.change_percent !== null &&
        marketSnapshot.change_percent !== undefined
          ? `${isPositive ? '+' : ''}${formatNumber(marketSnapshot.change_percent)}%`
          : 'N/A',
      icon: <Activity className="w-5 h-5" />,
      color: isPositive ? 'text-green-500' : isNegative ? 'text-red-500' : '',
    },
    {
      label: 'Volume',
      value: formatVolume(marketSnapshot.volume),
      icon: <BarChart3 className="w-5 h-5" />,
    },
    {
      label: 'High',
      value: `$${formatNumber(marketSnapshot.high)}`,
      icon: <TrendingUp className="w-5 h-5" />,
    },
    {
      label: 'Low',
      value: `$${formatNumber(marketSnapshot.low)}`,
      icon: <TrendingDown className="w-5 h-5" />,
    },
    {
      label: 'Open',
      value: `$${formatNumber(marketSnapshot.open)}`,
      icon: <DollarSign className="w-5 h-5" />,
    },
    {
      label: 'Prev Close',
      value: `$${formatNumber(marketSnapshot.prev_close)}`,
      icon: <DollarSign className="w-5 h-5" />,
    },
  ]

  return (
    <div className="bg-surface rounded-lg p-6">
      <div className="flex items-center justify-between mb-4">
        <h3 className="text-lg font-semibold">Market Metrics</h3>
        {marketSnapshot.timestamp && (
          <div className="flex items-center gap-2 text-sm text-muted">
            <Calendar className="w-4 h-4" />
            <span>{marketSnapshot.timestamp}</span>
            {marketSnapshot.market && (
              <span className="ml-2 px-2 py-0.5 bg-primary/10 text-primary rounded text-xs font-medium">
                {marketSnapshot.market}
              </span>
            )}
          </div>
        )}
      </div>

      <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
        {metrics.map((metric, idx) => (
          <div
            key={idx}
            className={`p-4 rounded-lg border transition-all ${
              metric.highlight
                ? 'bg-primary/5 border-primary/20 dark:bg-primary/10 dark:border-primary/30'
                : 'bg-background/50 border-border dark:bg-gray-800/50 dark:border-gray-700'
            }`}
          >
            <div className="flex items-center gap-2 mb-2">
              <div className={`${metric.color || 'text-muted'}`}>
                {metric.icon}
              </div>
              <span className="text-xs text-muted font-medium">
                {metric.label}
              </span>
            </div>
            <div
              className={`text-lg font-bold ${
                metric.color || 'text-foreground dark:text-white'
              }`}
            >
              {metric.value}
            </div>
          </div>
        ))}
      </div>
    </div>
  )
}

export default MarketMetricsCards
