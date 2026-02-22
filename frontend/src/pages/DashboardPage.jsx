// src/pages/DashboardPage.jsx
import React, { useState } from 'react'
import SearchBar from '../components/SearchBar'
import AnalysisPanel from '../components/AnalysisPanel'
import useSearch from '../hooks/useSearch'

const DashboardPage = () => {
  const { data, loading, error, runSearch } = useSearch()
  const [analysisData, setAnalysisData] = useState(null)

  const handleSearch = async (query) => {
    try {
      const res = await runSearch(query)
      setAnalysisData(res)
    } catch (err) {
      console.error('Search error', err)
    }
  }

  const finalData = analysisData || data

  return (
    <div className="bg-background w-full">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        {/* Header */}
        <div className="mb-8">
          <h1 className="text-3xl font-bold mb-2">Research Dashboard</h1>
          <p className="text-muted">Analyze stocks with AI-powered insights</p>
        </div>

        <SearchBar onSearch={handleSearch} />

        {loading && (
          <div className="mt-8 p-8 bg-surface rounded-lg text-center">
            <div className="inline-block animate-spin rounded-full h-8 w-8 border-b-2 border-primary"></div>
            <p className="mt-4 text-muted">Analyzing...</p>
          </div>
        )}

        {error && (
          <div className="mt-8 p-4 bg-error/10 border border-error/20 rounded-lg">
            <p className="text-error">Error: {error.message} </p>
          </div>
        )}

        {!loading && finalData && (
          <div className="mt-8">
            <AnalysisPanel data={finalData} />
          </div>
        )}
      </div>
    </div>
  )
}

export default DashboardPage
