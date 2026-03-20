import React, { useEffect, useState } from 'react'
import { useWatchlist } from '../context/WatchlistContext'
import apiClient from '../api/axios'

const Watchlist = () => {
  const { items, remove } = useWatchlist()
  const [prices, setPrices] = useState({})
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    const fetchPrices = async () => {
      if (items.length === 0) {
        setLoading(false)
        return
      }

      try {
        const responses = await Promise.all(
          items.map((item) =>
            apiClient
              .get(`/financial/price?symbol=${item.symbol}`)
              .then((res) => res.data)
          )
        )

        const priceMap = {}
        responses.forEach((data, index) => {
          priceMap[items[index].symbol] = data?.price ?? null
        })

        setPrices(priceMap)
      } catch (err) {
        console.error('Failed to fetch prices:', err)
      } finally {
        setLoading(false)
      }
    }

    fetchPrices()
  }, [items])

  if (items.length === 0) {
    return (
      <div className="p-6 bg-surface rounded-lg">
        <p className="text-muted">No items in your watchlist yet.</p>
      </div>
    )
  }

  return (
    <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-3">
      {items.map((item) => (
        <div
          key={item.symbol}
          className="p-5 bg-surface rounded-xl shadow-sm flex flex-col justify-between"
        >
          <div>
            <h2 className="text-lg font-semibold">{item.symbol}</h2>
            <p className="text-sm text-muted mb-3">{item.name}</p>

            {loading ? (
              <div className="h-6 w-24 bg-gray-300 animate-pulse rounded"></div>
            ) : (
              <p className="text-xl font-bold">
                {prices[item.symbol] !== null ? `₹${prices[item.symbol]}` : '-'}
              </p>
            )}
          </div>

          <button
            onClick={() => remove(item.symbol)}
            className="mt-4 text-sm text-red-500 hover:underline"
          >
            Remove
          </button>
        </div>
      ))}
    </div>
  )
}

export default Watchlist
