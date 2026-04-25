import React from 'react'
import { createContext, useContext, useState } from 'react'
import { dashboardSearchAPI } from '../api/dashboard'

export const SearchContext = createContext()

const CACHE_TTL = 60 * 1000 // 1 minute in milliseconds

export const SearchProvider = ({ children }) => {
  const [query, setQuery] = useState('')
  const [market, setMarket] = useState('US') // 'US' | 'INDIA'
  const [data, setData] = useState(() => {
    try {
      const cached = localStorage.getItem('eq_search_cache')

      if (!cached) {
        return null
      }

      const { results, timestamp } = JSON.parse(cached)
      const cacheAge = Date.now() - timestamp

      // Clear stale cache on mount
      if (cacheAge > CACHE_TTL) {
        localStorage.removeItem('eq_search_cache')
        return null
      }

      return results
    } catch {
      // Clear corrupted cache
      localStorage.removeItem('eq_search_cache')
      return null
    }
  })
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState(null)

  const runSearch = async (searchQuery, searchMarket = market) => {
    if (!searchQuery || searchQuery.trim().length === 0) return

    try {
      // Check if we have valid cached results for this query
      const cached = localStorage.getItem('eq_search_cache')

      if (cached) {
        const {
          query: cachedQuery,
          cachedMarket,
          results,
          timestamp,
        } = JSON.parse(cached)
        const cacheAge = Date.now() - timestamp

        // Reuse cache if same query, same market and within TTL
        if (
          cachedQuery === searchQuery &&
          cachedMarket === searchMarket &&
          cacheAge <= CACHE_TTL
        ) {
          setData(results)
          return
        }

        // Clear stale or mismatched cache
        if (
          cacheAge > CACHE_TTL ||
          cachedQuery !== searchQuery ||
          cachedMarket !== searchMarket
        ) {
          localStorage.removeItem('eq_search_cache')
        }
      }

      // Fetch fresh data
      setLoading(true)
      setError(null)

      const result = await dashboardSearchAPI(searchQuery, searchMarket)

      setData(result)

      // Store query, market with results and timestamp
      const cacheObject = {
        query: searchQuery,
        cachedMarket: searchMarket,
        results: result,
        timestamp: Date.now(),
      }
      localStorage.setItem('eq_search_cache', JSON.stringify(cacheObject))
    } catch (err) {
      setError(err.message || 'Something went wrong')
    } finally {
      setLoading(false)
    }
  }

  const clearResults = () => {
    setData(null)
    setQuery('')
    localStorage.removeItem('eq_search_cache')
  }

  return (
    <SearchContext.Provider
      value={{
        query,
        setQuery,
        market,
        setMarket,
        data,
        loading,
        error,
        runSearch,
        clearResults,
      }}
    >
      {children}
    </SearchContext.Provider>
  )
}

export const useSearch = () => useContext(SearchContext)
