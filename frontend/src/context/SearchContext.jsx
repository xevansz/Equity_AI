import React, { useEffect } from 'react'
import { createContext, useContext, useState } from 'react'
import apiClient from '../api/axios'

export const SearchContext = createContext()

export const SearchProvider = ({ children }) => {
  const [query, setQuery] = useState(() => {
    const storedQuery = localStorage.getItem('eq_search_query')
    return storedQuery || ''
  })
  const [data, setData] = useState(() => {
    const stored = localStorage.getItem('eq_search_results')
    return stored ? JSON.parse(stored) : null
  })
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState(null)

  useEffect(() => {
    localStorage.setItem('eq_search_query', query)
  }, [query])

  const runSearch = async (searchQuery) => {
    if (!searchQuery || searchQuery.trim().length === 0) return

    try {
      setLoading(true)
      setError(null)

      const res = await apiClient.post('/search', { query: searchQuery })
      const result = res.data

      setData(result)
      localStorage.setItem('eq_search_results', JSON.stringify(result))
    } catch (err) {
      setError(
        err.response?.data?.detail || err.message || 'Something went wrong'
      )
    } finally {
      setLoading(false)
    }
  }

  const clearResults = () => {
    setData(null)
    setQuery('')
    localStorage.removeItem('eq_search_query')
    localStorage.removeItem('eq_search_results')
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
