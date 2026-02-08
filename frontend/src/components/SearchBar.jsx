// SearchBar.jsx
import React, { useState } from 'react';
import { Search } from 'lucide-react';

const SearchBar = ({ onSearch }) => {
  const [query, setQuery] = useState('');

  const handleSubmit = (e) => {
    e.preventDefault();
    if (query.trim()) {
      onSearch(query);
    }
  };

  return (
    <form onSubmit={handleSubmit} className="w-full">
      <div className="relative">
        <Search className="absolute left-4 top-1/2 transform -translate-y-1/2 w-5 h-5 text-textMuted" />
        <input
          type="text"
          value={query}
          onChange={(e) => setQuery(e.target.value)}
          placeholder="Search for stocks (e.g., AAPL, Tesla, Microsoft)..."
          className="w-full pl-12 pr-4 py-4 bg-surface border border-textMuted/20 rounded-lg text-text placeholder-textMuted focus:outline-none focus:border-primary transition-colors"
        />
      </div>
    </form>
  );
};

export default SearchBar;