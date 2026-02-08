import React, { useState } from 'react';
import { useNavigate, Link } from 'react-router-dom';
import AuthLayout from './AuthLayout';
import useAuth from '../hooks/useAuth';
import * as authApi from '../api/auth';

const Register = () => {
  const navigate = useNavigate();
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [confirmPassword, setConfirmPassword] = useState('');

  const { login } = useAuth();

  const handleSubmit = (e) => {
    e.preventDefault();
    if (password !== confirmPassword) {
      alert('Passwords do not match');
      return;
    }
    (async () => {
      try {
        await authApi.register(email, password);
        // automatically log in after register
        await login(email, password);
        navigate('/dashboard');
      } catch (err) {
        console.error('Register failed', err);
        alert('Register failed: ' + (err.response?.data?.detail || err.message));
      }
    })();
  };

  return (
    <AuthLayout>
      <div className="max-w-md mx-auto">
        <h1 className="text-2xl font-bold mb-6">Create Account</h1>
        <form onSubmit={handleSubmit} className="space-y-4">
          <input
            type="email"
            placeholder="Email"
            value={email}
            onChange={(e) => setEmail(e.target.value)}
            className="w-full px-4 py-2 border border-textMuted/20 rounded-lg bg-surface text-text placeholder-textMuted focus:outline-none focus:border-primary"
            required
          />
          <input
            type="password"
            placeholder="Password"
            value={password}
            onChange={(e) => setPassword(e.target.value)}
            className="w-full px-4 py-2 border border-textMuted/20 rounded-lg bg-surface text-text placeholder-textMuted focus:outline-none focus:border-primary"
            required
          />
          <input
            type="password"
            placeholder="Confirm Password"
            value={confirmPassword}
            onChange={(e) => setConfirmPassword(e.target.value)}
            className="w-full px-4 py-2 border border-textMuted/20 rounded-lg bg-surface text-text placeholder-textMuted focus:outline-none focus:border-primary"
            required
          />
          <button
            type="submit"
            className="w-full px-4 py-2 bg-primary text-background font-semibold rounded-lg hover:bg-primaryDark transition-colors"
          >
            Sign Up
          </button>
        </form>
        <p className="text-sm text-textMuted mt-4">
          Already have an account? <Link to="/login" className="text-primary hover:underline">Sign in</Link>
        </p>
      </div>
    </AuthLayout>
  );
};

export default Register;
