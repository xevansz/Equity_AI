#!/usr/bin/env node

const fs = require('fs');
const path = require('path');

// Color scheme inspired by EquityAI
const colors = {
  primary: '#3DD9D0', // Turquoise
  primaryDark: '#2BB8B0',
  secondary: '#1A1F2E', // Dark navy
  background: '#0F1419',
  surface: '#1E2532',
  text: '#E8EAED',
  textMuted: '#9CA3AF',
  accent: '#60A5FA',
  success: '#10B981',
  warning: '#F59E0B',
  error: '#EF4444'
};

// Project structure
const structure = {
  'src/api': [
    'auth.js',
    'search.js'
  ],
  'src/auth': [
    'Login.jsx',
    'Register.jsx',
    'ForgotPassword.jsx',
    'ProtectedRoute.jsx',
    'AuthLayout.jsx'
  ],
  'src/components': [
    'Navbar.jsx',
    'Footer.jsx',
    'SearchBar.jsx',
    'StockCard.jsx',
    'Dashboard.jsx',
    'Watchlist.jsx',
    'AnalysisPanel.jsx',
    'RiskIndicator.jsx',
    'LoadingSpinner.jsx'
  ],
  'src/context': [
    'AuthContext.jsx',
    'ThemeContext.jsx'
  ],
  'src/hooks': [
    'useAuth.js',
    'useSearch.js'
  ],
  'src/pages': [
    'HomePage.jsx',
    'DashboardPage.jsx',
    'WatchlistPage.jsx'
  ],
  'src/styles': [
    'theme.js'
  ],
  'src': [
    'App.jsx',
    'main.jsx'
  ],
  'public': [
    'index.html'
  ],
  'docs': [
    'README.md',
    'SETUP.md',
    'API.md',
    'COMPONENTS.md',
    'DEPLOYMENT.md',
    'CONTRIBUTING.md',
    'CHANGELOG.md'
  ],
  'scripts': [
    'setup.js',
    'deploy.js'
  ],
  '.': [
    'package.json',
    'vite.config.js',
    'tailwind.config.js',
    'postcss.config.js',
    '.eslintrc.json',
    '.gitignore'
  ]
};

// File contents
const fileContents = {
  // Main files
  'src/main.jsx': `import React from 'react';
import ReactDOM from 'react-dom/client';
import App from './App';
import './styles/index.css';
import { AuthProvider } from './context/AuthContext';
import { ThemeProvider } from './context/ThemeContext';

ReactDOM.createRoot(document.getElementById('root')).render(
  <React.StrictMode>
    <ThemeProvider>
      <AuthProvider>
        <App />
      </AuthProvider>
    </ThemeProvider>
  </React.StrictMode>
);`,

  'src/App.jsx': `import React from 'react';
import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';
import Navbar from './components/Navbar';
import Footer from './components/Footer';
import HomePage from './pages/HomePage';
import DashboardPage from './pages/DashboardPage';
import WatchlistPage from './pages/WatchlistPage';
import Login from './auth/Login';
import Register from './auth/Register';
import ProtectedRoute from './auth/ProtectedRoute';

function App() {
  return (
    <Router>
      <div className="min-h-screen bg-background text-text flex flex-col">
        <Navbar />
        <main className="flex-grow">
          <Routes>
            <Route path="/" element={<HomePage />} />
            <Route path="/login" element={<Login />} />
            <Route path="/register" element={<Register />} />
            <Route
              path="/dashboard"
              element={
                <ProtectedRoute>
                  <DashboardPage />
                </ProtectedRoute>
              }
            />
            <Route
              path="/watchlist"
              element={
                <ProtectedRoute>
                  <WatchlistPage />
                </ProtectedRoute>
              }
            />
          </Routes>
        </main>
        <Footer />
      </div>
    </Router>
  );
}

export default App;`,

  // Pages
  'src/pages/HomePage.jsx': `import React from 'react';
import { Link } from 'react-router-dom';
import { TrendingUp, BarChart3, Shield, Zap } from 'lucide-react';

const HomePage = () => {
  const features = [
    {
      icon: <TrendingUp className="w-6 h-6" />,
      title: 'LLM-Powered Analysis',
      description: 'Advanced AI models analyze stocks in seconds'
    },
    {
      icon: <BarChart3 className="w-6 h-6" />,
      title: 'Real-time Data',
      description: 'Live market data and instant updates'
    },
    {
      icon: <Shield className="w-6 h-6" />,
      title: 'Risk Assessment',
      description: 'Comprehensive risk evaluation tools'
    },
    {
      icon: <Zap className="w-6 h-6" />,
      title: 'Instant Reports',
      description: 'Generate detailed reports instantly'
    }
  ];

  return (
    <div className="relative overflow-hidden">
      {/* Hero Section */}
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-20 md:py-32">
        <div className="text-center">
          <div className="mb-6 inline-flex items-center gap-2 px-4 py-2 rounded-full bg-surface border border-primary/20">
            <Zap className="w-4 h-4 text-primary" />
            <span className="text-sm text-textMuted">Powered by MCP Financial Data + LLMs</span>
          </div>
          
          <h1 className="text-5xl md:text-7xl font-bold mb-6">
            AI-Powered <span className="text-primary">Equity Research</span>
            <br />at Your Fingertips
          </h1>
          
          <p className="text-xl text-textMuted mb-12 max-w-3xl mx-auto">
            Transform your investment research with conversational AI. Get comprehensive
            stock analysis, valuation insights, and risk assessments in seconds—not hours.
          </p>
          
          <div className="flex flex-col sm:flex-row gap-4 justify-center">
            <Link
              to="/register"
              className="px-8 py-4 bg-primary hover:bg-primaryDark text-background font-semibold rounded-lg transition-colors inline-flex items-center justify-center gap-2"
            >
              Start Researching
              <span>→</span>
            </Link>
            <button className="px-8 py-4 bg-surface hover:bg-surface/80 text-text font-semibold rounded-lg border border-textMuted/20 transition-colors">
              View Demo
            </button>
          </div>
        </div>

        {/* Features Grid */}
        <div className="mt-32 grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
          {features.map((feature, index) => (
            <div
              key={index}
              className="p-6 bg-surface rounded-xl border border-textMuted/10 hover:border-primary/30 transition-colors"
            >
              <div className="w-12 h-12 bg-primary/10 rounded-lg flex items-center justify-center text-primary mb-4">
                {feature.icon}
              </div>
              <h3 className="text-lg font-semibold mb-2">{feature.title}</h3>
              <p className="text-textMuted text-sm">{feature.description}</p>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
};

export default HomePage;`,

  'src/pages/DashboardPage.jsx': `import React, { useState } from 'react';
import SearchBar from '../components/SearchBar';
import Dashboard from '../components/Dashboard';
import AnalysisPanel from '../components/AnalysisPanel';

const DashboardPage = () => {
  const [selectedStock, setSelectedStock] = useState(null);
  const [analysisData, setAnalysisData] = useState(null);

  const handleSearch = async (query) => {
    // API call would go here
    console.log('Searching for:', query);
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
            <AnalysisPanel data={analysisData} />
          </div>
        </div>
      </div>
    </div>
  );
};

export default DashboardPage;`,

  'src/pages/WatchlistPage.jsx': `import React from 'react';
import Watchlist from '../components/Watchlist';

const WatchlistPage = () => {
  return (
    <div className="min-h-screen bg-background">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        <div className="mb-8">
          <h1 className="text-3xl font-bold mb-2">Watchlist</h1>
          <p className="text-textMuted">Track your favorite stocks</p>
        </div>
        
        <Watchlist />
      </div>
    </div>
  );
};

export default WatchlistPage;`,

  // Components
  'src/components/Navbar.jsx': `import React from 'react';
import { Link } from 'react-router-dom';
import { TrendingUp, Menu } from 'lucide-react';
import { useAuth } from '../hooks/useAuth';

const Navbar = () => {
  const { user, logout } = useAuth();

  return (
    <nav className="bg-secondary border-b border-textMuted/10">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="flex justify-between items-center h-16">
          <Link to="/" className="flex items-center gap-3">
            <div className="w-10 h-10 bg-primary rounded-xl flex items-center justify-center">
              <TrendingUp className="w-6 h-6 text-background" />
            </div>
            <div>
              <h1 className="text-xl font-bold">EquityAI</h1>
              <p className="text-xs text-textMuted">Research Assistant</p>
            </div>
          </Link>

          <div className="hidden md:flex items-center gap-8">
            <Link to="/dashboard" className="text-text hover:text-primary transition-colors">
              Dashboard
            </Link>
            <Link to="/watchlist" className="text-text hover:text-primary transition-colors">
              Watchlist
            </Link>
            
            {user ? (
              <div className="flex items-center gap-4">
                <span className="text-textMuted">{user.email}</span>
                <button
                  onClick={logout}
                  className="px-4 py-2 bg-surface hover:bg-surface/80 rounded-lg transition-colors"
                >
                  Sign Out
                </button>
              </div>
            ) : (
              <div className="flex items-center gap-4">
                <Link to="/login" className="text-text hover:text-primary transition-colors">
                  Sign In
                </Link>
                <Link
                  to="/register"
                  className="px-6 py-2 bg-primary hover:bg-primaryDark text-background font-semibold rounded-lg transition-colors"
                >
                  Get Started
                </Link>
              </div>
            )}
          </div>

          <button className="md:hidden">
            <Menu className="w-6 h-6" />
          </button>
        </div>
      </div>
    </nav>
  );
};

export default Navbar;`,

  'src/components/SearchBar.jsx': `import React, { useState } from 'react';
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

export default SearchBar;`,

  // Styles
  'src/styles/theme.js': `export const theme = {
  colors: {
    primary: '#3DD9D0',
    primaryDark: '#2BB8B0',
    secondary: '#1A1F2E',
    background: '#0F1419',
    surface: '#1E2532',
    text: '#E8EAED',
    textMuted: '#9CA3AF',
    accent: '#60A5FA',
    success: '#10B981',
    warning: '#F59E0B',
    error: '#EF4444'
  },
  spacing: {
    xs: '0.25rem',
    sm: '0.5rem',
    md: '1rem',
    lg: '1.5rem',
    xl: '2rem',
    '2xl': '3rem'
  },
  borderRadius: {
    sm: '0.375rem',
    md: '0.5rem',
    lg: '0.75rem',
    xl: '1rem',
    full: '9999px'
  }
};`,

  // Configuration
  'package.json': `{
  "name": "equityai-frontend",
  "version": "1.0.0",
  "type": "module",
  "scripts": {
    "dev": "vite",
    "build": "vite build",
    "preview": "vite preview",
    "lint": "eslint src --ext js,jsx",
    "setup": "node scripts/setup.js"
  },
  "dependencies": {
    "react": "^18.2.0",
    "react-dom": "^18.2.0",
    "react-router-dom": "^6.20.0",
    "axios": "^1.6.2",
    "lucide-react": "^0.294.0",
    "recharts": "^2.10.3"
  },
  "devDependencies": {
    "@vitejs/plugin-react": "^4.2.1",
    "vite": "^5.0.8",
    "tailwindcss": "^3.4.0",
    "postcss": "^8.4.32",
    "autoprefixer": "^10.4.16",
    "eslint": "^8.56.0",
    "eslint-plugin-react": "^7.33.2"
  }
}`,

  'vite.config.js': `import { defineConfig } from 'vite';
import react from '@vitejs/plugin-react';

export default defineConfig({
  plugins: [react()],
  server: {
    port: 3000,
    open: true
  },
  build: {
    outDir: 'dist',
    sourcemap: true
  }
});`,

  'tailwind.config.js': `/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
  ],
  theme: {
    extend: {
      colors: {
        primary: '#3DD9D0',
        primaryDark: '#2BB8B0',
        secondary: '#1A1F2E',
        background: '#0F1419',
        surface: '#1E2532',
        text: '#E8EAED',
        textMuted: '#9CA3AF',
        accent: '#60A5FA',
        success: '#10B981',
        warning: '#F59E0B',
        error: '#EF4444'
      },
      fontFamily: {
        sans: ['Inter', 'system-ui', 'sans-serif']
      }
    },
  },
  plugins: [],
}`,

  'public/index.html': `<!DOCTYPE html>
<html lang="en">
  <head>
    <meta charset="UTF-8" />
    <link rel="icon" type="image/svg+xml" href="/vite.svg" />
    <meta name="viewport" content="width=device-width, initial-scale=1.0" />
    <title>EquityAI - AI-Powered Equity Research</title>
    <link rel="preconnect" href="https://fonts.googleapis.com">
    <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
    <link href="https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800&display=swap" rel="stylesheet">
  </head>
  <body>
    <div id="root"></div>
    <script type="module" src="/src/main.jsx"></script>
  </body>
</html>`,

  '.gitignore': `# Dependencies
node_modules/
.pnp
.pnp.js

# Testing
coverage/

# Production
dist/
build/

# Misc
.DS_Store
.env
.env.local
.env.development.local
.env.test.local
.env.production.local

# Logs
npm-debug.log*
yarn-debug.log*
yarn-error.log*
pnpm-debug.log*

# IDE
.vscode/
.idea/
*.swp
*.swo
*~`,

  'docs/README.md': `# EquityAI Frontend

AI-Powered Equity Research Platform

## Features

- 🤖 LLM-powered stock analysis
- 📊 Real-time market data
- 🛡️ Risk assessment tools
- ⚡ Instant report generation
- 📱 Responsive design

## Quick Start

\`\`\`bash
npm install
npm run dev
\`\`\`

## Documentation

- [Setup Guide](./SETUP.md)
- [API Documentation](./API.md)
- [Component Library](./COMPONENTS.md)
- [Deployment Guide](./DEPLOYMENT.md)

## Tech Stack

- React 18
- Vite
- TailwindCSS
- React Router
- Axios
- Lucide Icons

## License

MIT`
};

// Create directory structure and files
function createStructure() {
  console.log('🚀 Creating EquityAI Frontend Structure...\n');

  Object.keys(structure).forEach(dir => {
    const fullPath = path.join(process.cwd(), dir);
    if (!fs.existsSync(fullPath)) {
      fs.mkdirSync(fullPath, { recursive: true });
      console.log(`📁 Created: ${dir}`);
    }

    structure[dir].forEach(file => {
      const filePath = path.join(fullPath, file);
      const content = fileContents[path.join(dir, file).replace(/\\/g, '/')] || 
                     `// ${file}\n// TODO: Implement this ${file.endsWith('.jsx') ? 'component' : 'file'}\n`;
      
      fs.writeFileSync(filePath, content);
      console.log(`  ✅ ${file}`);
    });
  });

  // Create additional required files
  const cssContent = `@tailwind base;
@tailwind components;
@tailwind utilities;

* {
  margin: 0;
  padding: 0;
  box-sizing: border-box;
}

body {
  font-family: 'Inter', sans-serif;
  -webkit-font-smoothing: antialiased;
  -moz-osx-font-smoothing: grayscale;
}`;

  fs.mkdirSync(path.join(process.cwd(), 'src/styles'), { recursive: true });
  fs.writeFileSync(path.join(process.cwd(), 'src/styles/index.css'), cssContent);

  console.log('\n✨ Frontend structure created successfully!');
  console.log('\n📦 Next steps:');
  console.log('  1. npm install');
  console.log('  2. npm run dev');
  console.log('  3. Open http://localhost:3000\n');
}

createStructure();