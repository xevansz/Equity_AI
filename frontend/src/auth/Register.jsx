import React, { useState } from 'react'
import { useNavigate, Link } from 'react-router-dom'
import AuthLayout from './AuthLayout'
import useAuth from '../hooks/useAuth'
import * as authApi from '../api/auth'
import { validateRegisterForm } from './validate'

const Register = () => {
  const navigate = useNavigate()
  const [email, setEmail] = useState('')
  const [password, setPassword] = useState('')
  const [confirmPassword, setConfirmPassword] = useState('')
  const [errors, setErrors] = useState({})

  const { login } = useAuth()

  const handleSubmit = async (e) => {
    e.preventDefault()

    const validateErrors = validateRegisterForm(email, password, confirmPassword)

    if (Object.keys(validateErrors).length > 0) {
      setErrors(validateErrors)
      return
    }

    try {
      await authApi.register(email, password)
      // automatically log in after register
      await login(email, password)
      navigate('/dashboard')
    } catch (err) {
      console.error('Register failed', err)
      setErrors({
        general: err.response?.data?.detail || err.message || 'registration failed',
      })
    }
  }

  return (
    <AuthLayout>
      <div className="max-w-md mx-auto">
        <h1 className="text-2xl font-bold mb-6">Create Account</h1>
        <form onSubmit={handleSubmit} className="space-y-4">
          <input
            type="email"
            placeholder="Email"
            value={email}
            onChange={(e) => {
              setEmail(e.target.value)
              if (errors.email) setErrors({ ...errors, email: '' })
            }}
            className={`w-full px-4 py-2 border rounded-lg bg-surface text-text placeholder-textMuted focus:outline-none focus:border-primary ${
              errors.email ? 'border-error' : 'border-textMuted/20'
            }`}
          />
          {errors.email && <p className="text-error text-sm mt-1">{errors.email}</p>}

          <input
            type="password"
            placeholder="Password"
            value={password}
            onChange={(e) => {
              setPassword(e.target.value)
              if (errors.password) setErrors({ ...errors, password: '' })
            }}
            className={`w-full px-4 py-2 border rounded-lg bg-surface text-text placeholder-textMuted focus:outline-none focus:border-primary ${
              errors.password ? 'border-error' : 'border-textMuted/20'
            }`}
            required
          />
          {errors.password && <p className="text-error text-sm mt-1">{errors.password}</p>}

          <input
            type="password"
            placeholder="Confirm Password"
            value={confirmPassword}
            onChange={(e) => {
              setConfirmPassword(e.target.value)
              if (errors.confirmPassword) setErrors({ ...errors, confirmPassword: '' })
            }}
            className={`w-full px-4 py-2 border rounded-lg bg-surface text-text placeholder-textMuted focus:outline-none focus:border-primary ${
              errors.confirmPassword ? 'border-error' : 'border-textMuted/20'
            }`}
            required
          />
          {errors.confirmPassword && (
            <p className="text-error text-sm mt-1">{errors.confirmPassword}</p>
          )}

          <button
            type="submit"
            className="w-full px-4 py-2 bg-primary text-background font-semibold rounded-lg hover:bg-primaryDark transition-colors"
          >
            Sign Up
          </button>
        </form>

        {errors.general && (
          <div className="p-3 bg-error/10 border border-error/20 rounded-lg">
            <p className="text-error text-sm">{errors.general}</p>
          </div>
        )}

        <p className="text-sm text-textMuted mt-4">
          Already have an account?{' '}
          <Link to="/login" className="text-primary hover:underline">
            Sign in
          </Link>
        </p>
      </div>
    </AuthLayout>
  )
}

export default Register
