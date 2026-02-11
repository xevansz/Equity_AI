// Navbar.jsx
import React from 'react';
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
            {user ? (
              <>
                <Link to="/dashboard" className="text-text hover:text-primary transition-colors">
                  Dashboard
                </Link>
                <Link to="/watchlist" className="text-text hover:text-primary transition-colors">
                  Watchlist
                </Link>
                <Link to="/chat" className="text-text hover:text-primary transition-colors">
                  Chat
                </Link>
                <div className="flex items-center gap-4">
                  <span className="text-textMuted">{user.email}</span>
                  <button
                    onClick={logout}
                    className="px-4 py-2 bg-surface hover:bg-surface/80 rounded-lg transition-colors"
                  >
                    Sign Out
                  </button>
                </div>
              </>
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

export default Navbar;