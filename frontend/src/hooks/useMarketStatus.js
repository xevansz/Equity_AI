import { useEffect, useState, useCallback } from 'react'

/**
 * Market hours configuration
 * All times in UTC for consistency
 */
const MARKET_HOURS = {
  US: {
    open: { hour: 14, minute: 30 }, // 9:30 AM EST (14:30 UTC)
    close: { hour: 21, minute: 0 }, // 4:00 PM EST (21:00 UTC)
    timezone: 'America/New_York',
  },
  INDIA: {
    open: { hour: 3, minute: 45 }, // 9:15 AM IST (03:45 UTC)
    close: { hour: 10, minute: 0 }, // 3:30 PM IST (10:00 UTC)
    timezone: 'Asia/Kolkata',
  },
}

/**
 * Hook to check if a market is currently open
 * @param {string} market - 'US' or 'INDIA'
 * @returns {object} - { isOpen, nextOpenTime, status, marketLabel }
 */
export function useMarketStatus(market = 'US') {
  const [status, setStatus] = useState({
    isOpen: false,
    nextOpenTime: null,
    status: 'unknown',
    marketLabel: market,
  })

  const checkMarketStatus = useCallback(() => {
    const now = new Date()
    const config = MARKET_HOURS[market]

    if (!config) {
      return {
        isOpen: false,
        status: 'unknown',
        nextOpenTime: null,
        marketLabel: market,
      }
    }

    const currentUTCHour = now.getUTCHours()
    const currentUTCMinute = now.getUTCMinutes()
    const currentMinutes = currentUTCHour * 60 + currentUTCMinute

    const openMinutes = config.open.hour * 60 + config.open.minute
    const closeMinutes = config.close.hour * 60 + config.close.minute

    const dayOfWeek = now.getUTCDay() // 0 = Sunday, 6 = Saturday

    // Check if it's a weekday
    const isWeekday = dayOfWeek >= 1 && dayOfWeek <= 5

    // Check if market is open
    let isOpen = false
    let marketStatus = 'closed'

    if (isWeekday) {
      if (currentMinutes >= openMinutes && currentMinutes <= closeMinutes) {
        isOpen = true
        marketStatus = 'open'
      } else if (currentMinutes < openMinutes) {
        marketStatus = 'pre_market'
      } else {
        marketStatus = 'after_hours'
      }
    } else {
      marketStatus = 'weekend'
    }

    // Calculate next open time
    let nextOpenTime = null
    if (!isOpen) {
      const nextOpen = new Date(now)

      if (!isWeekday || currentMinutes > closeMinutes) {
        // Move to next weekday
        const daysUntilMonday = dayOfWeek === 0 ? 1 : 8 - dayOfWeek
        nextOpen.setUTCDate(nextOpen.getUTCDate() + daysUntilMonday)
      }

      nextOpen.setUTCHours(config.open.hour, config.open.minute, 0, 0)
      nextOpenTime = nextOpen.toISOString()
    }

    return {
      isOpen,
      status: marketStatus,
      nextOpenTime,
      marketLabel: market === 'US' ? 'US Markets' : 'Indian Markets',
      hoursLabel:
        market === 'US' ? '9:30 AM - 4:00 PM EST' : '9:15 AM - 3:30 PM IST',
    }
  }, [market])

  useEffect(() => {
    const updateStatus = () => {
      setStatus(checkMarketStatus())
    }

    // Initial check
    updateStatus()

    // Update every minute
    const interval = setInterval(updateStatus, 60 * 1000)

    return () => clearInterval(interval)
  }, [checkMarketStatus])

  return status
}

/**
 * Get status badge color and label
 * @param {string} status - market status
 * @returns {object} - { color, label, pulse }
 */
export function getMarketStatusDisplay(status) {
  switch (status) {
    case 'open':
      return { color: 'green', label: 'Live', pulse: true }
    case 'pre_market':
      return { color: 'yellow', label: 'Pre-Market', pulse: false }
    case 'after_hours':
      return { color: 'orange', label: 'After Hours', pulse: false }
    case 'weekend':
      return { color: 'gray', label: 'Closed', pulse: false }
    default:
      return { color: 'gray', label: 'Unknown', pulse: false }
  }
}
