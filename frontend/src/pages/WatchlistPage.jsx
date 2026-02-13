import React from 'react'
import Watchlist from '../components/Watchlist'

const WatchlistPage = () => {
  return (
    <div className="bg-background w-full">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        <div className="mb-8">
          <h1 className="text-3xl font-bold mb-2">Watchlist</h1>
          <p className="text-muted">Track your favorite stocks</p>
        </div>

        <Watchlist />
      </div>
    </div>
  )
}

export default WatchlistPage
