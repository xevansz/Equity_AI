import React from 'react'
import { Search, Globe } from 'lucide-react'

const SearchBar = ({
  query,
  setQuery,
  onSearch,
  loading,
  market,
  setMarket,
}) => {
  const handleSubmit = (e) => {
    e.preventDefault()
    if (query.trim()) {
      onSearch(query)
    }
  }

  const markets = [
    { id: 'US', label: '🇺🇸 US', placeholder: 'AAPL, Tesla, Microsoft...' },
    {
      id: 'INDIA',
      label: '🇮🇳 India',
      placeholder: 'RELIANCE, TCS, HDFC Bank...',
    },
  ]

  const activeMarket = markets.find((m) => m.id === market) || markets[0]

  return (
    <form onSubmit={handleSubmit} className="w-full">
      <div className="mb-3 flex items-center gap-2">
        <Globe className="w-4 h-4 text-muted" />
        <div className="flex bg-surface border border-text-muted/20 rounded-lg p-1">
          {markets.map((m) => (
            <button
              key={m.id}
              type="button"
              onClick={() => setMarket(m.id)}
              className={`px-3 py-1 text-sm font-medium rounded-md transition-colors ${
                market === m.id
                  ? 'bg-primary text-white'
                  : 'text-text-muted hover:text-text hover:bg-text-muted/10'
              }`}
            >
              {m.label}
            </button>
          ))}
        </div>
      </div>
      <div className="relative flex gap-2">
        <div className="relative flex-1">
          <Search className="absolute left-4 top-1/2 transform -translate-y-1/2 w-5 h-5 text-muted" />
          <input
            type="text"
            value={query}
            onChange={(e) => setQuery(e.target.value)}
            placeholder={`Search for stocks (e.g., ${activeMarket.placeholder})`}
            className="w-full pl-12 pr-4 py-2 bg-surface border border-text-muted/20 rounded-lg text-text placeholder-text-muted focus:outline-none focus:border-primary transition-colors"
          />
        </div>
        <button
          type="submit"
          disabled={loading || !query.trim()}
          className="px-2 bg-primary text-white rounded-lg hover:opacity-90 transition-opacity disabled:opacity-50 disabled:cursor-not-allowed"
        >
          {loading ? 'Searching...' : 'Search'}
        </button>
      </div>
    </form>
  )
}

export default SearchBar
