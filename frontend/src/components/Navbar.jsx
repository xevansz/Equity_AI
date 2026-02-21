// Navbar.jsx
import React, { useState } from 'react'
import { Link } from 'react-router-dom'
import { TrendingUp, Menu, X } from 'lucide-react'
import { useAuth } from '../hooks/useAuth'
import ThemeToggle from './ThemeToggle'

const Navbar = () => {
  const { user, logout } = useAuth()
  const [isMobileMenuOpen, setIsMobileMenuOpen] = useState(false)

  return (
    <nav className="bg-surface border-b border-text-muted/10">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="flex justify-between items-center h-16">
          <Link to={user ? '/dashboard' : '/'} className="flex items-center gap-3">
            <div className="w-10 h-10 bg-primary rounded-xl flex items-center justify-center">
              <TrendingUp className="w-6 h-6 text-background" />
            </div>
            <div>
              <h1 className="text-xl font-bold text-text">EquityAI</h1>
              <p className="text-xs text-muted">Research Assistant</p>
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
                  <ThemeToggle />
                  <span className="text-muted">{user.email}</span>
                  <button
                    onClick={logout}
                    className="px-4 py-2 bg-surface hover:bg-surface/80 rounded-lg transition-colors text-text"
                  >
                    Sign Out
                  </button>
                </div>
              </>
            ) : (
              <div className="flex items-center gap-4">
                <ThemeToggle />
                <Link to="/login" className="text-text hover:text-primary transition-colors">
                  Sign In
                </Link>
                <Link
                  to="/register"
                  className="px-6 py-2 bg-primary hover:bg-primary/80 text-background font-semibold rounded-lg transition-colors"
                >
                  Get Started
                </Link>
              </div>
            )}
          </div>

          <button
            className="md:hidden p-2 rounded-lg hover:bg-surface dark:hover:bg-surface transition-colors"
            onClick={() => setIsMobileMenuOpen(!isMobileMenuOpen)}
            aria-label="Toggle mobile menu"
          >
            {isMobileMenuOpen ? (
              <X className="w-6 h-6 text-text" />
            ) : (
              <Menu className="w-6 h-6 text-text" />
            )}
          </button>
        </div>

        {/* Mobile Menu */}
        {isMobileMenuOpen && (
          <div className="md:hidden bg-secondary dark:bg-secondary border-t border-text-muted/10">
            <div className="px-4 py-4 space-y-4">
              {user ? (
                <>
                  <Link
                    to="/dashboard"
                    className="block text-text hover:text-primary transition-colors py-2"
                    onClick={() => setIsMobileMenuOpen(false)}
                  >
                    Dashboard
                  </Link>
                  <Link
                    to="/watchlist"
                    className="block text-text hover:text-primary transition-colors py-2"
                    onClick={() => setIsMobileMenuOpen(false)}
                  >
                    Watchlist
                  </Link>
                  <Link
                    to="/chat"
                    className="block text-text hover:text-primary transition-colors py-2"
                    onClick={() => setIsMobileMenuOpen(false)}
                  >
                    Chat
                  </Link>
                  <div className="pt-4 border-t border-text-muted/10">
                    <p className="text-muted text-sm mb-3">{user.email}</p>
                    <button
                      onClick={() => {
                        logout()
                        setIsMobileMenuOpen(false)
                      }}
                      className="w-full px-4 py-2 bg-surface hover:bg-surface/80 rounded-lg transition-colors text-text text-left"
                    >
                      Sign Out
                    </button>
                  </div>
                </>
              ) : (
                <>
                  <Link
                    to="/login"
                    className="block text-text hover:text-primary transition-colors py-2"
                    onClick={() => setIsMobileMenuOpen(false)}
                  >
                    Sign In
                  </Link>
                  <Link
                    to="/register"
                    className="block w-full px-6 py-2 bg-primary hover:bg-primary/80 text-background font-semibold rounded-lg transition-colors text-center"
                    onClick={() => setIsMobileMenuOpen(false)}
                  >
                    Get Started
                  </Link>
                </>
              )}
            </div>
          </div>
        )}
      </div>
    </nav>
  )
}

export default Navbar
