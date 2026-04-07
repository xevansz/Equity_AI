<div align="center">
    <h1>【 Equity AI 】</h1>
</div>

An LLM-powered real-time knowledge curation system for financial intelligence.

## Overview
## How it works  
## Configuration

Add your API keys to `.env`:

```env
# Required
ALPHA_VANTAGE_API_KEY=your_alpha_vantage_key

# Optional - for fallback support
FINNHUB_API_KEY=your_finnhub_key
```

## Installation
## Equity
## customizing doc ingestion pipeline  
## Datasets(Docs)
## Paper
## Acknowledgement
## Citations

## RAG System (`rag/`)

`query_expander.py` - ⚠️ Dead code — kept as placeholder for future multi-query RAG

### Hybrid Routing (`services/chat_service.py`)

| Intent           | Path                                              |
| ---------------- | ------------------------------------------------- |
| `research_query` | RAG pipeline → Gemini with doc context            |
| `general_query`  | RAG pipeline → Gemini with doc context            |
| `price_query`    | API-only → Gemini (no RAG overhead)               |
| `financial_query`| API-only → Gemini (no RAG overhead)               |
| `news_query`     | API-only → Gemini (no RAG overhead)               |

---

## Things to do
1. **Add API rate limiting** middleware (slowapi or similar)
2. **Explicit repo layer** isolate persistant logic from services. ingestion may fetch apis
    Build Explicit repo layer:
        *Services(symbolcacheservice) directly calls monogdb
        *memory probably does DB ops
### WebSocket Endpoint
**URL:** `ws://localhost:8000/api/ws/stream`

**Client Protocol:**
```javascript
// Subscribe to symbols
ws.send({
  action: "subscribe",
  symbols: ["AAPL", "TSLA"],
  market: "US",
  interval: "1min"
})

// Unsubscribe
ws.send({
  action: "unsubscribe",
  symbols: ["AAPL"]
})

// Heartbeat
ws.send({ action: "ping" })
```

**Server Messages:**
```javascript
// Quote update
{
  type: "quote",
  symbol: "AAPL",
  data: {
    symbol: "AAPL",
    price: 175.43,
    change: 2.15,
    change_percent: 1.24,
    volume: 52341234,
    high: 176.20,
    low: 173.80,
    open: 174.00,
    prev_close: 173.28,
    timestamp: "2024-01-15T14:30:00",
    market: "US"
  }
}

// Pong response
{ type: "pong", timestamp: "..." }

// Error
{ type: "error", symbol: "...", message: "..." }
```

### REST API Endpoint
**URL:** `POST /api/stock`

Unified search endpoint for initial data fetch (fundamentals, chart, depth).

## Configuration

### Environment Variables
Add to `.env`:
```bash
# TwelveData API keys (comma-separated for rotation)
TWELVE_DATA_API_KEYS=key1,key2,key3

# Upstox API keys (comma-separated for rotation)
UPSTOX_API_KEYS=key1,key2

# Existing keys (used as fallback)
ALPHA_VANTAGE_API_KEY=your_key
FINNHUB_API_KEY=your_key
```

### Key Rotation
- **TwelveData:** 800 requests/day per key (free tier)
- **Upstox:** 1000 requests/day per key
- Automatic rotation on rate limits
- Daily usage reset at midnight UTC

## Testing

### Backend
```bash
# Start the server
cd backend
python -m uvicorn app.main:app --reload

# Check WebSocket health
curl http://localhost:8000/api/ws/health
```

### Frontend
```bash
# Start the dev server
cd frontend
npm run dev

# Test Dashboard
# 1. Search for a symbol (e.g., "AAPL")
# 2. Verify "Live" indicator appears
# 3. Watch price updates every 2 seconds

# Test Watchlist
# 1. Add symbols to watchlist
# 2. Navigate to Watchlist page
# 3. Verify "Live" indicators and price updates
```

### WebSocket Test (Manual)
```javascript
const ws = new WebSocket('ws://localhost:8000/api/ws/stream')

ws.onopen = () => {
  ws.send(JSON.stringify({
    action: 'subscribe',
    symbols: ['AAPL', 'TSLA'],
    market: 'US'
  }))
}

ws.onmessage = (event) => {
  console.log('Received:', JSON.parse(event.data))
}
```

## Future Enhancements

1. **Candle Data Streaming:** Add OHLCV candle updates to WebSocket
2. **Market Depth:** Real-time order book for Indian stocks
3. **News Alerts:** Push notifications for breaking news
4. **Custom Intervals:** User-configurable update frequencies
5. **Historical Replay:** Replay past market data for backtesting

## Troubleshooting

### WebSocket Not Connecting
- Check backend is running on port 8000
- Verify CORS settings in main.py
- Check browser console for connection errors

### No Real-Time Updates
- Verify API keys are configured in .env
- Check backend logs for provider errors
- Ensure symbols are valid for the market

### Rate Limit Errors
- Add more API keys for rotation
- Reduce update frequency
- Check daily usage limits