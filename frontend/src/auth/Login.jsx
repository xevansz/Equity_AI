//frontend/src/auth/Login.jsx
import React, { useState } from 'react';
import { useNavigate, Link } from 'react-router-dom';
import useAuth from '../hooks/useAuth';
import AuthLayout from './AuthLayout';

const Login = () => {
  const navigate = useNavigate();
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');

  const { login } = useAuth();

  const handleSubmit = (e) => {
    e.preventDefault();
    (async () => {
      try {
        await login(email, password);
        navigate('/dashboard');
      } catch (err) {
        console.error('Login failed', err);
        alert('Login failed: ' + (err.response?.data?.detail || err.message));
      }
    })();
  };

  return (
    <AuthLayout>
      <div className="max-w-md mx-auto">
        <h1 className="text-2xl font-bold mb-6">Sign In</h1>
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
          <button
            type="submit"
            className="w-full px-4 py-2 bg-primary text-background font-semibold rounded-lg hover:bg-primaryDark transition-colors"
          >
            Sign In
          </button>
        </form>
        <p className="text-sm text-textMuted mt-4">
          Don't have an account? <Link to="/register" className="text-primary hover:underline">Sign up</Link>
        </p>
      </div>
    </AuthLayout>
  );
};

export default Login;
