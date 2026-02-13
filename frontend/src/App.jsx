//frontend/src/App.jsx
import React from 'react'
import { RouterProvider, createBrowserRouter, Outlet } from 'react-router-dom'
import Navbar from './components/Navbar'
import Footer from './components/Footer'
import HomePage from './pages/HomePage'
import DashboardPage from './pages/DashboardPage'
import WatchlistPage from './pages/WatchlistPage'
import ChatPage from './pages/ChatPage'
import Login from './auth/Login'
import Register from './auth/Register'
import ProtectedRoute from './auth/ProtectedRoute'

const Layout = () => (
  <div className="min-h-screen bg-background text-text flex flex-col">
    <Navbar />
    <main className="flex-grow">
      <Outlet />
    </main>
    <Footer />
  </div>
)

const router = createBrowserRouter(
  [
    {
      element: <Layout />,
      children: [
        { path: '/', element: <HomePage /> },
        { path: '/login', element: <Login /> },
        { path: '/register', element: <Register /> },
        {
          path: '/dashboard',
          element: (
            <ProtectedRoute>
              <DashboardPage />
            </ProtectedRoute>
          ),
        },
        {
          path: '/watchlist',
          element: (
            <ProtectedRoute>
              <WatchlistPage />
            </ProtectedRoute>
          ),
        },
        {
          path: '/chat',
          element: (
            <ProtectedRoute>
              <ChatPage />
            </ProtectedRoute>
          ),
        },
      ],
    },
  ],
  {
    future: {
      v7_startTransition: true,
      v7_relativeSplatPath: true,
    },
  }
)

function App() {
  return <RouterProvider router={router} />
}

export default App
