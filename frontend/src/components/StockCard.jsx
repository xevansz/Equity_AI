import React from 'react'

const StockCard = ({ symbol = '-', name = '-', price = '-' }) => {
  return (
    <div className="p-4 bg-surface rounded-lg border border-text-muted/8">
      <div className="flex justify-between items-center">
        <div>
          <div className="text-sm text-muted">{symbol}</div>
          <div className="font-semibold">{name}</div>
        </div>
        <div className="text-right">
          <div className="font-medium">{price}</div>
        </div>
      </div>
    </div>
  )
}

export default StockCard
