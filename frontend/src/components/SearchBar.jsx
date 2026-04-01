import React from 'react'
import { Search } from 'lucide-react'

const SearchBar = ({ query, setQuery, onSearch, loading }) => {
  const handleSubmit = (e) => {
    e.preventDefault()
    if (query.trim()) {
      onSearch(query)
    }
  }

  return (
    <form onSubmit={handleSubmit} className="w-full">
      <div className="relative flex gap-2 border-red-50">
        <div className="relative flex-1">
          <Search className="absolute left-4 top-1/2 transform -translate-y-1/2 w-5 h-5 text-muted" />
          <input
            type="text"
            value={query}
            onChange={(e) => setQuery(e.target.value)}
            placeholder="Search for stocks (e.g., AAPL, Tesla, Microsoft)..."
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
