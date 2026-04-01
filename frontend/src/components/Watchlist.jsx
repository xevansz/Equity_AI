import React, { useEffect, useState } from 'react'
import { useWatchlist } from '../context/WatchlistContext'
import apiClient from '../api/axios'

const Watchlist = () => {
  const { items, remove } = useWatchlist()
  const [priceData, setPriceData] = useState({})
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

        const dataMap = {}
        responses.forEach((data, index) => {
          dataMap[items[index].symbol] = {
            price: data?.price ?? null,
            market: data?.market ?? null,
            status: data?.status ?? null,
          }
        })

        setPriceData(dataMap)
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
            <div className="flex items-center gap-2 mb-1">
              <h2 className="text-lg font-semibold">{item.symbol}</h2>
              {!loading && priceData[item.symbol]?.market && (
                <span className="px-2 py-0.5 bg-primary/10 text-primary rounded text-xs font-medium">
                  {priceData[item.symbol].market}
                  {priceData[item.symbol].status &&
                    ` • ${priceData[item.symbol].status}`}
                </span>
              )}
            </div>
            <p className="text-sm text-muted mb-3">{item.name}</p>

            {loading ? (
              <div className="h-6 w-24 bg-gray-300 animate-pulse rounded"></div>
            ) : (
              <p className="text-xl font-bold">
                {priceData[item.symbol]?.price !== null
                  ? `₹${priceData[item.symbol].price}`
                  : '-'}
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
