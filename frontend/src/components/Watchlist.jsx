import React from 'react'

const Watchlist = ({ items = [] }) => {
  return (
    <div className="p-4 bg-surface rounded-lg">
      <h2 className="text-lg font-semibold mb-2">Watchlist</h2>
      {items.length === 0 ? (
        <p className="text-muted">No items in your watchlist yet.</p>
      ) : (
        <ul className="space-y-2">
          {items.map((it) => (
            <li key={it.symbol} className="flex justify-between">
              <span>
                {it.symbol} — {it.name}
              </span>
              <span className="text-muted">{it.price ?? '-'}</span>
            </li>
          ))}
        </ul>
      )}
    </div>
  )
}

export default Watchlist
