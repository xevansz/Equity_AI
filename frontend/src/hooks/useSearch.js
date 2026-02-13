//useSearch.js
import { useState, useCallback } from 'react'
import { searchAPI } from '../api/search'

export default function useSearch() {
  const [data, setData] = useState(null)
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState(null)

  const runSearch = useCallback(async (query, symbol = null) => {
    setLoading(true)
    setError(null)
    try {
      const res = await searchAPI(query, symbol)
      setData(res)
      return res
    } catch (err) {
      setError(err)
      throw err
    } finally {
      setLoading(false)
    }
  }, [])

  return { data, loading, error, runSearch }
}
