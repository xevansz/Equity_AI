<div align="center">
    <h1>【 Equity AI 】</h1>
</div>

An LLM-powered real-time knowledge curation system for financial intelligence.

## Overview
## How it works  
## Configuration

## Implemented Features

### Authentication
| Feature | Status | Details |
|---------|--------|---------|
| User auth (JWT) | ✅ Working | `auth/` module with `get_current_user` dependency |
| Admin-only endpoints | ✅ Working | `admin_only` dependency guards ingestion API |

### Market Data
| Feature | Status | Details |
|---------|--------|---------|
| Stock quote (US + India) | ✅ Working | Unified dispatcher via TwelveData / Upstox |
| Intraday candlestick chart | ✅ Working | `GET /api/stock`, `dispatcher.get_chart()` |
| Live WebSocket stream | ✅ Working | `ws_stream.py` — subscribe/unsubscribe per symbol, 2s refresh |
| Market fundamentals | ✅ Working | `dispatcher.get_fundamentals()` |
| Market depth (India only) | ✅ Working | `dispatcher.get_market_depth()` |
| Batch stock search | ✅ Working | `POST /api/batch` — parallel multi-symbol fetch |
| Auto market detection | ✅ Working | `resolve_market_from_symbol()` in `utils/market_resolver.py` |
| API key rotation | ✅ Working | `KeyRotatorRegistry` for TwelveData and Upstox |
| Market status banner | ✅ Working | `get_market_status()` utility |

### Dashboard
| Feature | Status | Details |
|---------|--------|---------|
| Dashboard search | ✅ Working | `POST /api/dashboard/search` — symbol resolver + stock + news in parallel |
| LLM symbol resolver | ✅ Working | `symbol_resolver.py` uses Gemini to resolve company names to tickers |
| Market snapshot cards | ✅ Working | `extract_market_snapshot()` in `market_snapshot_service.py` |

### News
| Feature | Status | Details |
|---------|--------|---------|
| News fetching & display | ✅ Working | `NewsLoader` fetches from NewsAPI, stores in MongoDB |
| News caching (MongoDB) | ✅ Working | Articles upserted into `ingested_documents` collection |
| News cache warmer | ✅ Working | `warmer.py` background task refreshes news every 15 min for watchlisted symbols |

### Watchlist
| Feature | Status | Details |
|---------|--------|---------|
| Add/remove symbols | ✅ Working | `POST/DELETE /api/watchlist` |
| Paginated watchlist fetch | ✅ Working | `GET /api/watchlist` with cursor-based pagination |

### Conversational Chat
| Feature | Status | Details |
|---------|--------|---------|
| Chat endpoint | ✅ Working | `POST /api/chat` — routed through `ChatService` |
| Intent detection | ✅ Working | `intent_detector.py` classifies price/financial/news/research/general |
| Query routing | ✅ Working | `query_router.py` maps intent → service path |
| Conversation memory (save) | ✅ Working | `memory.py` persists messages to MongoDB per session |
| Conversation history (load) | ✅ Working | `GET /api/conversations/{session_id}` |
| Session listing & deletion | ✅ Working | `GET/DELETE /api/conversations` |
| **Follow-up context** | ✅ Working | `get_context()` is called and history is passed to Gemini multi-turn |
| Chat response caching | ✅ Working | LRU cache with TTL (1h, 100 entries) — first messages only to prevent cross-session leakage |
| Chat UI sidebar | ✅ Working | Session list, new chat, delete chat in `ChatPage.jsx` |

### Document Ingestion Infrastructure
| Feature | Status | Details |
|---------|--------|---------|
| Earnings transcript loader | ✅ Working | `TranscriptLoader` fetches and stores in MongoDB |
| Transcript cache warmer | ✅ Working | `warmer.py` pre-fetches current + previous quarter every 6h |
| SEC filing loader (10-K/10-Q) | ✅ Working | `SECFilingLoader` via `sec_api.py` |
| Admin ingest endpoint | ✅ Working | `POST /api/admin/ingest/{symbol}` — transcripts + SEC filing + embed |
| Admin reindex endpoint | ✅ Working | `POST /api/admin/reindex/{symbol}` — re-chunks from MongoDB into Chroma |
| Vector chunker | ✅ Working | `chunker.py` — `chunk_text()` |
| ChromaDB vector store | ✅ Working | `VectorStore` with `SentenceTransformerEmbeddingFunction` |
| Document upsert | ✅ Working | `VectorIngestionService._embed_docs()` with chunk-level IDs and metadata |

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