import React, { useState } from 'react'
import { useNavigate, Link } from 'react-router-dom'
import useAuth from '../hooks/useAuth'
import AuthLayout from './AuthLayout'
import { validateLoginForm } from './validate'

const Login = () => {
  const navigate = useNavigate()
  const [email, setEmail] = useState('')
  const [password, setPassword] = useState('')
  const [errors, setErrors] = useState({})

  const { login } = useAuth()

  const handleSubmit = async (e) => {
    e.preventDefault()

    const validateErrors = validateLoginForm(email, password)

    if (Object.keys(validateErrors).length > 0) {
      setErrors(validateErrors)
      return
    }

    try {
      await login(email, password)
      navigate('/dashboard')
    } catch (err) {
      console.error('Login failed', err)
      setErrors({
        general: err.response?.data?.detail || err.message || 'login failed',
      })
    }
  }

  return (
    <AuthLayout>
      <div className="max-w-md mx-auto">
        <h1 className="text-2xl font-bold mb-6 text-text">Sign In</h1>
        <form onSubmit={handleSubmit} className="space-y-4">
          <input
            type="email"
            placeholder="Email"
            value={email}
            onChange={(e) => {
              setEmail(e.target.value)
              if (errors.email) setErrors({ ...errors, email: '' })
            }}
            className={`w-full px-4 py-2 border rounded-lg bg-surface text-text placeholder-light-text-muted dark:placeholder-dark-text-muted focus:outline-none focus:border-primary ${
              errors.email ? 'border-error' : 'border-text-muted/20'
            }`}
          />
          {errors.email && (
            <p className="text-error text-sm mt-1">{errors.email}</p>
          )}

          <input
            type="password"
            placeholder="Password"
            value={password}
            onChange={(e) => {
              setPassword(e.target.value)
              if (errors.password) setErrors({ ...errors, password: '' })
            }}
            className={`w-full px-4 py-2 border rounded-lg bg-surface text-text placeholder-light-text-muted dark:placeholder-dark-text-muted focus:outline-none focus:border-primary ${
              errors.password ? 'border-error' : 'border-text-muted/20'
            }`}
          />

          <button
            type="submit"
            className="w-full px-4 py-2 bg-primary text-background font-semibold rounded-lg hover:bg-primary/80 transition-colors"
          >
            Sign In
          </button>
        </form>
        {errors.general && (
          <div className="p-3 bg-error/10 border border-error/20 rounded-lg">
            <p className="text-error text-sm">{errors.general}</p>
          </div>
        )}
        <div className="flex flex-row flex-wrap gap-2 mt-4 justify-center">
          <p className="text-sm text-muted">
            <Link
              to="/forgot-password"
              className="text-primary hover:underline"
            >
              Forgot Password?
            </Link>
          </p>
          <p className="text-sm text-blue-500"> &middot; </p>
          <p className="text-sm text-muted">
            <Link to="/register" className="text-primary hover:underline">
              Sign up
            </Link>
          </p>
        </div>
      </div>
    </AuthLayout>
  )
}

export default Login
