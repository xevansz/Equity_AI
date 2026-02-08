// DashboardPage.jsx
import React, { useState } from 'react';
import SearchBar from '../components/SearchBar';
import Dashboard from '../components/Dashboard';
import AnalysisPanel from '../components/AnalysisPanel';
import useSearch from '../hooks/useSearch';


const DashboardPage = () => {
  const [selectedStock, setSelectedStock] = useState(null);
  const [analysisData, setAnalysisData] = useState(null);
  const { data, loading, error, runSearch } = useSearch();

  const handleSearch = async (query) => {
    try {
      const res = await runSearch(query);
      setAnalysisData(res);
    } catch (err) {
      console.error('Search error', err);
    }
  };

  return (
    <div className="min-h-screen bg-background">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        <div className="mb-8">
          <h1 className="text-3xl font-bold mb-2">Research Dashboard</h1>
          <p className="text-textMuted">Analyze stocks with AI-powered insights</p>
        </div>

        <SearchBar onSearch={handleSearch} />
        
        <div className="mt-8 grid grid-cols-1 lg:grid-cols-3 gap-6">
          <div className="lg:col-span-2">
            <Dashboard selectedStock={selectedStock} />
          </div>
          <div>
            <AnalysisPanel data={analysisData || data} />
          </div>
        </div>
      </div>
    </div>
  );
};

export default DashboardPage;