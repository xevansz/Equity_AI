// src/context/AuthContext.jsx
import React, { createContext, useState, useEffect } from 'react';
import axios from 'axios';
import * as authApi from '../api/auth';

export const AuthContext = createContext({
  user: null,
  login: async () => {},
  logout: () => {},
  loading: true,
});

export function AuthProvider({ children }) {
  const [user, setUser] = useState(null);
  const [token, setToken] = useState(() => localStorage.getItem('token'));
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    // 🚨 No token → do NOT call backend
    if (!token) {
      delete axios.defaults.headers.common.Authorization;
      setUser(null);
      setLoading(false);
      return;
    }

    axios.defaults.headers.common.Authorization = `Bearer ${token}`;

    authApi
      .me()
      .then((u) => setUser(u))
      .catch(() => {
        // Token invalid / backend unavailable
        setUser(null);
        setToken(null);
        localStorage.removeItem('token');
        delete axios.defaults.headers.common.Authorization;
      })
      .finally(() => setLoading(false));
  }, [token]);

  const login = async (email, password) => {
    const data = await authApi.login(email, password);

    if (!data?.access_token) {
      throw new Error('Login failed');
    }

    localStorage.setItem('token', data.access_token);
    setToken(data.access_token);
    axios.defaults.headers.common.Authorization = `Bearer ${data.access_token}`;

    const u = await authApi.me();
    setUser(u);
    return u;
  };

  const logout = () => {
    setUser(null);
    setToken(null);
    localStorage.removeItem('token');
    delete axios.defaults.headers.common.Authorization;
  };

  return (
    <AuthContext.Provider value={{ user, login, logout, loading }}>
      {children}
    </AuthContext.Provider>
  );
}

export default AuthProvider;
