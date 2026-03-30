import React, { useEffect } from 'react'
import { createContext, useContext, useState } from 'react'
import { dashboardSearchAPI } from '../api/dashboard'

export const SearchContext = createContext()

const CACHE_TTL = 60 * 1000 // 1 minute in milliseconds

export const SearchProvider = ({ children }) => {
  const [query, setQuery] = useState(() => {
    const storedQuery = localStorage.getItem('eq_search_query')
    return storedQuery || ''
  })
  const [data, setData] = useState(() => {
    try {
      const stored = localStorage.getItem('eq_search_results')
      const storedTs = localStorage.getItem('eq_search_results_ts')
      const storedQuery = localStorage.getItem('eq_search_query')

      if (!stored || !storedTs || !storedQuery) {
        return null
      }

      const cacheAge = Date.now() - Number(storedTs)

      // Clear stale cache on mount
      if (cacheAge > CACHE_TTL) {
        localStorage.removeItem('eq_search_results')
        localStorage.removeItem('eq_search_results_ts')
        return null
      }

      return JSON.parse(stored)
    } catch {
      // Clear corrupted cache
      localStorage.removeItem('eq_search_results')
      localStorage.removeItem('eq_search_results_ts')
      return null
    }
  })
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState(null)

  useEffect(() => {
    localStorage.setItem('eq_search_query', query)
  }, [query])

  const runSearch = async (searchQuery) => {
    if (!searchQuery || searchQuery.trim().length === 0) return

    try {
      // Check if we have valid cached results for this query
      const cachedResults = localStorage.getItem('eq_search_results')
      const cachedTs = localStorage.getItem('eq_search_results_ts')
      const cachedQuery = localStorage.getItem('eq_search_query')

      if (cachedResults && cachedTs && cachedQuery) {
        const cacheAge = Date.now() - Number(cachedTs)

        // Reuse cache if same query and within TTL
        if (cachedQuery === searchQuery && cacheAge <= CACHE_TTL) {
          const parsedData = JSON.parse(cachedResults)
          setData(parsedData)
          return
        }

        // Clear stale or mismatched cache
        if (cacheAge > CACHE_TTL || cachedQuery !== searchQuery) {
          localStorage.removeItem('eq_search_results')
          localStorage.removeItem('eq_search_results_ts')
        }
      }

      // Fetch fresh data
      setLoading(true)
      setError(null)

      const result = await dashboardSearchAPI(searchQuery)

      setData(result)
      localStorage.setItem('eq_search_results', JSON.stringify(result))
      localStorage.setItem('eq_search_results_ts', String(Date.now()))
    } catch (err) {
      setError(err.message || 'Something went wrong')
    } finally {
      setLoading(false)
    }
  }

  const clearResults = () => {
    setData(null)
    setQuery('')
    localStorage.removeItem('eq_search_query')
    localStorage.removeItem('eq_search_results')
    localStorage.removeItem('eq_search_results_ts')
  }

  return (
    <SearchContext.Provider
      value={{
        query,
        setQuery,
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
