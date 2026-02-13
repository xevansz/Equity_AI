import React, { useState } from 'react'

const tabs = [
  { key: 'thesis', label: '🧠 Thesis' },
  { key: 'data', label: '📊 Data' },
  { key: 'risk', label: '⚠️ Risk' },
]

const InsightTabs = ({ thesis, data, risk }) => {
  const [active, setActive] = useState('thesis')

  const contentMap = {
    thesis,
    data,
    risk,
  }

  return (
    <div className="bg-surface rounded-xl border border-textMuted/10 p-4">
      {/* Tabs */}
      <div className="flex gap-2 mb-4">
        {tabs.map((t) => (
          <button
            key={t.key}
            onClick={() => setActive(t.key)}
            className={`px-4 py-1.5 rounded-lg text-sm font-medium transition ${
              active === t.key
                ? 'bg-primary text-background'
                : 'bg-background text-textMuted hover:text-text'
            }`}
          >
            {t.label}
          </button>
        ))}
      </div>

      {/* Content */}
      <div className="text-sm whitespace-pre-line text-text">
        {contentMap[active] || 'No data available'}
      </div>
    </div>
  )
}

export default InsightTabs
