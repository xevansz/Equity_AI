// src/components/Dashboard.jsx
import React, { useState } from 'react';
import SearchBar from './SearchBar';
import AnalysisPanel from './AnalysisPanel';

const Dashboard = () => {
  const [query, setQuery] = useState('');

  return (
    <div className="space-y-8">

      {/* ONLY SEARCH BAR IN ENTIRE DASHBOARD */}
      <SearchBar onSearch={setQuery} />

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">

        {/* Market Overview */}
        

        {/* Analysis */}
        <AnalysisPanel data={null} />
      </div>
    </div>
  );
};

export default Dashboard;
