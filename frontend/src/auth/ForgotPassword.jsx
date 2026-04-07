import React, { useState } from 'react'
import { Link } from 'react-router-dom'
import AuthLayout from './AuthLayout'
import apiClient from '../api/axios'

const ForgotPassword = () => {
  const [step, setStep] = useState('email')
  const [email, setEmail] = useState('')
  const [otp, setOtp] = useState('')
  const [newPassword, setNewPassword] = useState('')
  const [error, setError] = useState(null)
  const [loading, setLoading] = useState(false)

  const handleSubmit = async (e) => {
    e.preventDefault()
    setError(null)
    setLoading(true)

    // OTP
    try {
      await apiClient.post('/api/auth/forgot-password', { email })
      setStep('otp')
    } catch (err) {
      setError(err.response?.data?.detail || 'Something went wrong')
    } finally {
      setLoading(false)
    }
  }

  const handleReset = async (e) => {
    e.preventDefault()
    setError(null)
    setLoading(true)

    // OTP
    try {
      await apiClient.post('/api/auth/reset-password', {
        email,
        otp,
        new_password: newPassword,
      })
      setStep('success')
    } catch (err) {
      setError(err.response?.data?.detail || 'Invalid or expired OTP.')
    } finally {
      setLoading(false)
    }
  }

  return (
    <AuthLayout>
      <div className="max-w-md mx-auto">
        <h1 className="text-2xl font-bold mb-6">Reset Password</h1>

        {/* Send otp */}
        {step === 'email' && (
          <form onSubmit={handleSubmit} className="space-y-4">
            <input
              type="email"
              placeholder="Enter your email"
              value={email}
              onChange={(e) => setEmail(e.target.value)}
              className="w-full px-4 py-2 border border-text-muted/20 rounded-lg bg-surface text-text placeholder-text-muted focus:outline-none focus:border-primary"
              required
            />
            {error && <p className="text-error text-sm mt-1">{error}</p>}
            <button
              type="submit"
              disabled={loading}
              className="w-full px-4 py-2 bg-primary text-background font-semibold rounded-lg hover:bg-primaryDark transition-colors"
            >
              {loading ? 'Sending...' : 'Send OTP'}
            </button>
            <p className="text-sm text-muted mt-4">
              <Link to="/login" className="text-primary hover:underline">
                Back to Sign In
              </Link>
            </p>
          </form>
        )}

        {/* Otp + new password */}
        {step === 'otp' && (
          <form onSubmit={handleReset} className="space-y-4">
            <p>
              OTP sent to <strong>{email}</strong>
            </p>
            <input
              type="text"
              placeholder="Enter OTP"
              value={otp}
              onChange={(e) => setOtp(e.target.value)}
              className="w-full px-4 py-2 border border-text-muted/20 rounded-lg bg-surface text-text placeholder-text-muted focus:outline-none focus:border-primary"
              required
            />
            <input
              type="password"
              placeholder="New password"
              value={newPassword}
              onChange={(e) => setNewPassword(e.target.value)}
              className="w-full px-4 py-2 border border-text-muted/20 rounded-lg bg-surface text-text placeholder-text-muted focus:outline-none focus:border-primary"
              required
            />
            {error && <p className="text-error text-sm mt-1">{error}</p>}
            <button
              type="submit"
              disabled={loading}
              className="w-full px-4 py-2 bg-primary text-background font-semibold rounded-lg hover:bg-primaryDark transition-colors"
            >
              {loading ? 'Resetting...' : 'Reset Password'}
            </button>
          </form>
        )}

        {/* Success message */}
        {step === 'success' && (
          <div className="space-y-4">
            <p className="text-green-500 text-sm">
              Password reset successfully!{' '}
              <Link to="/login" className="text-primary hover:underline">
                Sign in
              </Link>
            </p>
          </div>
        )}
      </div>
    </AuthLayout>
  )
}

export default ForgotPassword
