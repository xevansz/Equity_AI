//frontend/src/pages/HomePage.jsx
import React from 'react'
import { useNavigate } from 'react-router-dom'
import { TrendingUp, BarChart3, Shield, Zap } from 'lucide-react'
import useAuth from '../hooks/useAuth'

const HomePage = () => {
  const navigate = useNavigate()
  const { user } = useAuth()

  const handleStartResearching = () => {
    if (user) {
      navigate('/chat')
    } else {
      navigate('/login')
    }
  }
  const features = [
    {
      icon: <TrendingUp className="w-6 h-6" />,
      title: 'LLM-Powered Analysis',
      description: 'Advanced AI models analyze stocks in seconds',
    },
    {
      icon: <BarChart3 className="w-6 h-6" />,
      title: 'Real-time Data',
      description: 'Live market data and instant updates',
    },
    {
      icon: <Shield className="w-6 h-6" />,
      title: 'Risk Assessment',
      description: 'Comprehensive risk evaluation tools',
    },
    {
      icon: <Zap className="w-6 h-6" />,
      title: 'Instant Reports',
      description: 'Generate detailed reports instantly',
    },
  ]

  return (
    <div className="relative overflow-hidden bg-background w-full">
      {/* Hero Section */}
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-20 md:py-32">
        <div className="text-center">
          <div className="mb-6 inline-flex items-center gap-2 px-4 py-2 rounded-full bg-surface border border-text-muted/20">
            <Zap className="w-4 h-4 text-primary" />
            <span className="text-sm text-muted">Powered by MCP Financial Data + LLMs</span>
          </div>

          <h1 className="text-5xl md:text-7xl font-bold mb-6 text-text">
            AI-Powered <span className="text-primary">Equity Research</span>
            <br />
            at Your Fingertips
          </h1>

          <p className="text-xl text-muted mb-12 max-w-3xl mx-auto">
            Transform your investment research with conversational AI. Get comprehensive stock
            analysis, valuation insights, and risk assessments in seconds—not hours.
          </p>

          <div className="flex flex-col sm:flex-row gap-4 justify-center">
            <button
              onClick={handleStartResearching}
              className="px-8 py-4 bg-primary hover:bg-primary/80 text-background font-semibold rounded-lg transition-colors inline-flex items-center justify-center gap-2"
            >
              Start Researching
              <span>→</span>
            </button>
            <button className="px-8 py-4 bg-surface hover:bg-surface/80 text-text font-semibold rounded-lg border border-text-muted/20 transition-colors">
              View Demo
            </button>
          </div>
        </div>

        {/* Features Grid */}
        <div className="mt-16 grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
          {features.map((feature, index) => (
            <div
              key={index}
              className="p-6 bg-surface rounded-xl border border-text-muted/10 hover:border-primary/30 transition-colors"
            >
              <div className="w-12 h-12 bg-primary/10 rounded-lg flex items-center justify-center text-primary mb-4">
                {feature.icon}
              </div>
              <h3 className="text-lg font-semibold mb-0 text-text">{feature.title}</h3>
              <p className="text-muted text-sm">{feature.description}</p>
            </div>
          ))}
        </div>
      </div>
    </div>
  )
}

export default HomePage
