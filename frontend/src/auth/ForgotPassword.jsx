import React, { useState } from 'react';
import { Link } from 'react-router-dom';
import AuthLayout from './AuthLayout';

const ForgotPassword = () => {
  const [email, setEmail] = useState('');
  const [sent, setSent] = useState(false);

  const handleSubmit = (e) => {
    e.preventDefault();
    // TODO: Implement password reset logic
    console.log('Reset email:', email);
    setSent(true);
  };

  return (
    <AuthLayout>
      <div className="max-w-md mx-auto">
        <h1 className="text-2xl font-bold mb-6">Reset Password</h1>
        {sent ? (
          <div className="p-4 bg-primary/10 rounded-lg text-center">
            <p className="text-sm">Reset link sent to {email}</p>
            <p className="text-xs text-textMuted mt-2">Check your email for instructions.</p>
          </div>
        ) : (
          <form onSubmit={handleSubmit} className="space-y-4">
            <input
              type="email"
              placeholder="Email"
              value={email}
              onChange={(e) => setEmail(e.target.value)}
              className="w-full px-4 py-2 border border-textMuted/20 rounded-lg bg-surface text-text placeholder-textMuted focus:outline-none focus:border-primary"
              required
            />
            <button
              type="submit"
              className="w-full px-4 py-2 bg-primary text-background font-semibold rounded-lg hover:bg-primaryDark transition-colors"
            >
              Send Reset Link
            </button>
          </form>
        )}
        <p className="text-sm text-textMuted mt-4">
          <Link to="/login" className="text-primary hover:underline">Back to Sign In</Link>
        </p>
      </div>
    </AuthLayout>
  );
};

export default ForgotPassword;
