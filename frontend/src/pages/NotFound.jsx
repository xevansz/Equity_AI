import React from 'react'
import { Link } from 'react-router-dom'
import { Home } from 'lucide-react'
import { useAuth } from '../hooks/useAuth'

const PageNotFound = () => {
  const user = useAuth().user
  return (
    <div className="min-h-screen flex items-center justify-center px-6 bg-background text-text">
      <div className="text-center max-w-md">
        <h1 className="text-7xl font-bold">404</h1>

        <h2 className="mt-4 text-2xl font-semibold">Page not found</h2>

        <p className="mt-2 text-text-muted">
          The page you are looking for does not exist.
        </p>

        <Link
          to={user ? '/dashboard' : '/'}
          className="mt-8 inline-flex items-center gap-2 px-5 py-2 rounded-xl bg-primary text-background hover:bg-accent transition"
        >
          <Home size={18} />
          Return Home
        </Link>
      </div>
    </div>
  )
}

export default PageNotFound
