# EquityAI — Features

> What's implemented, what's a stub, and what's left to build.

---

## Product Vision

**EquityAI** is an LLM-powered real-time knowledge curation system for financial intelligence.

Three core surfaces:
1. **Dashboard** — Quick stock overview (price chart, key metrics, news)
2. **Watchlist** — Track favorite stocks with live price cards + market status
3. **Chat** — Deep-dive conversational research powered by RAG + LLM

---

## Page-by-Page Feature Status

### 1. Dashboard (`/dashboard`)

**Goal**: Search a stock → see a Groww-style price chart (red/green, 30-day), key metrics, significant news, and data from external APIs. Lighthearted, quick-glance view.

| Feature | Status | Details |
| --------- | -------- | --------- |
| Search bar | ✅ Done | Calls unified `/api/search`, resolves company name → ticker via LLM |
| AI chat answer | ✅ Done | Gemini response shown in "Thesis" tab |
| Financial data fetch | ✅ Done | Alpha Vantage income statement, balance sheet, cash flow |
| Key metrics calculation | ✅ Done | Revenue, EPS, ROE, ROA, Operating Margin, D/E, Current Ratio, FCF |
| Revenue/Profit line chart | ✅ Done | Recharts LineChart, last 5 years annual data |
| News articles | ✅ Done | NewsAPI fetches latest articles for symbol |
| Research report tabs | ✅ Done | Thesis / Data / Risk tabs in AnalysisPanel |
| Raw API response viewer | ✅ Done | JSON dump in left panel (dev tool, should be removed for prod) |
| **Stock price chart (Groww-style)** | ❌ Missing | No current/historical price data — Alpha Vantage doesn't provide this on free tier. Need a price API (yfinance, Finnhub, or Alpha Vantage TIME_SERIES) |
| **Price with red/green indicators** | ❌ Missing | No price change data |
| **30-day / timeframe selector** | ❌ Missing | No time-series data at all |
| **Market status indicator** | ❌ Missing | No market open/closed detection |
| **Formatted metric cards** | ❌ Missing | Metrics exist in data but displayed as raw JSON, not as styled cards |
| **News cards with sentiment** | ❌ Missing | News articles returned raw, no formatting or sentiment scoring |
| **Add to watchlist button** | ❌ Missing | No way to save stocks from dashboard |

### 2. Watchlist (`/watchlist`)

**Goal**: Show saved stocks as small cards with current price. Market status notice at bottom.

| Feature | Status | Details |
| --------- | -------- | --------- |
| Watchlist page | ✅ Done | Page exists with `Watchlist` component |
| Watchlist component | ✅ Done | Renders list of items with symbol, name, price |
| **Backend watchlist API** | ❌ Missing | No endpoints to add/remove/list watchlist items |
| **MongoDB watchlist collection** | ❌ Missing | No database storage for user watchlists |
| **Stock cards with live price** | ❌ Missing | Component accepts props but nothing feeds it data |
| **Current price fetching** | ❌ Missing | No price API integration |
| **Market status notice** | ❌ Missing | No market open/closed detection or display |
| **Add/remove stocks** | ❌ Missing | No UI for managing watchlist |
| **Per-user watchlists** | ❌ Missing | No user association |

### 3. Chat (`/chat`)

**Goal**: Deep-dive financial research. RAG-powered conversational interface that retrieves from a knowledge base of financial theories, studies, SEC filings, reports, etc. The core product.

| Feature | Status | Details |
| --------- | -------- | --------- |
| Chat UI | ✅ Done | Message bubbles, auto-scroll, input bar, send button |
| Send message → get response | ✅ Done | Calls `/api/search` → gets Gemini answer |
| Loading indicator | ✅ Done | Spinner while processing |
| Error handling | ✅ Done | Error messages displayed in chat |
| Markdown cleaning | ✅ Done | Strips bold/italic/headers from LLM response |
| In-memory response cache | ✅ Done | Same query returns cached answer |
| Rate limiting | ✅ Done | 6s minimum between Gemini calls |
| Conversation memory (backend) | ✅ Done | Messages saved to MongoDB `conversations` collection |
| **RAG retrieval from knowledge base** | ❌ Not working | ChromaDB is empty — no documents ingested. RAG pipeline runs but returns nothing, so Gemini answers without context |
| **Knowledge base ingestion** | ❌ Missing | No pipeline to ingest financial theories, studies, SEC filings, textbooks, etc. |
| **SEC filing retrieval** | ❌ Missing | SEC API is a stub |
| **Earnings transcript retrieval** | ❌ Missing | Transcript loader is a stub |
| **Source citations** | ❌ Missing | `sources: []` always returned empty |
| **Conversation history in UI** | ❌ Missing | Backend saves history but frontend doesn't load previous messages |
| **Session management** | ❌ Missing | All chats use `session_id: "default"` — no separate conversations |
| **Follow-up context** | ❌ Missing | Each message is independent — no conversation context sent to LLM |
| **Intent-based routing** | ❌ Not wired | Intent detector and query router exist but are never called |
| **Deep financial analysis** | ❌ Stubs | Research engine functions return placeholder text, not real analysis |

### 4. Home Page (`/`)

| Feature | Status | Details |
| --------- | -------- | --------- |
| Hero section | ✅ Done | Title, subtitle, CTA buttons |
| Feature cards | ✅ Done | 4 feature highlights |
| "Start Researching" button | ✅ Done | Routes to `/chat` if logged in, `/login` if not |
| "View Demo" button | ⚠️ Placeholder | Button exists but does nothing |
| Footer | ✅ Done | Shown on home, login, register pages |

### 5. Authentication

| Feature | Status | Details |
| --------- | -------- | --------- |
| Register | ✅ Done | Email + password with validation (8 chars, uppercase, number, special char) |
| Login | ✅ Done | JWT token stored in localStorage |
| Auto-login on refresh | ✅ Done | Token validated via `/api/auth/me` on mount |
| Logout | ✅ Done | Clears token, redirects |
| Admin login | ✅ Done | Env-based admin bypass |
| Protected routes | ✅ Done | Redirects to `/login` if not authenticated |
| Forgot password (backend) | ✅ Done | OTP generation + SMTP email |
| Reset password (backend) | ✅ Done | OTP verification + password update |
| **Forgot password (frontend)** | ⚠️ Exists but not routed | `ForgotPassword.jsx` exists, not in App.jsx routes, and doesn't call backend API |
| **Google OAuth** | ❌ Missing | Config fields exist but no implementation |

### 6. UI/UX

| Feature | Status | Details |
| --------- | -------- | --------- |
| Dark/light theme | ✅ Done | CSS variables + ThemeContext + localStorage persistence |
| Responsive navbar | ✅ Done | Desktop + mobile hamburger menu |
| Logo routing | ✅ Done | Goes to `/dashboard` when logged in, `/` when not |
| Loading states | ✅ Done | Spinners on dashboard and chat |
| Error states | ✅ Done | Error messages on dashboard and chat |
| **Consistent design system** | ⚠️ Partial | Color tokens defined, but some components use hardcoded colors |

---

## Backend Feature Status

### Research Engine (`research_engine/`)

**All analysis functions are stubs returning template strings.** The class-based analyzers below each function also exist but are never called.

| Component | What it does now | What it should do |
| --------- | -------- | --------- |
| `financial_analysis.py` | Returns static bullet points | Calculate real ratios from Alpha Vantage data (margins, ROE, ROA, liquidity) |
| `growth_analysis.py` | Returns static bullet points | Compute YoY revenue/earnings growth from historical statements |
| `valuation.py` | Returns static bullet points | PE ratio, DCF, relative valuation using real data |
| `risk_analysis.py` | Returns static bullet points | Beta, volatility, leverage-based risk scoring |
| `report_generator.py` | Calls the 4 stubs above, returns dict | Should use real data + optionally LLM for narrative |

### Financial Metrics (`services/financial_metrics.py`)
- ✅ Calculates 9 real metrics from Alpha Vantage data
- ⚠️ PE Ratio always `None` (needs market price)
- These metrics are **the only real calculations** in the entire backend

### Symbol Resolution (`llm/symbol_resolver.py`)
- ✅ Fully working — LLM extracts ticker from natural language
- ✅ MongoDB caching with aliases
- ✅ Fallback to "UNKNOWN"

---

## Features To Build — Prioritized

### Phase 1: Make Core Work (Chat + RAG)
*This is the heart of the product.*

1. **Build document ingestion pipeline**
   - Ingest financial textbooks, theories, studies into ChromaDB
   - Chunk documents properly
   - Fix embedder import bug
   - Create a script/endpoint to seed the knowledge base

2. **Fix RAG pipeline**
   - With documents in ChromaDB, retrieval will actually return context
   - Gemini will answer grounded in real knowledge instead of hallucinating

3. **Add conversation context**
   - Send last N messages to Gemini so it can do follow-ups
   - Load conversation history in frontend on page load

4. **Session management**
   - Generate unique session IDs per conversation
   - Allow users to start new conversations / view old ones

5. **Source citations**
   - Track which documents were retrieved
   - Display sources in chat UI

### Phase 2: Make Dashboard Useful

6. **Stock price API**
   - Integrate yfinance or Finnhub for current + historical prices
   - Backend endpoint: `GET /api/price/{symbol}?range=30d`

7. **Price chart component**
   - Groww-style area chart with red (down) / green (up) coloring
   - Timeframe selector (1D, 1W, 1M, 3M, 1Y)

8. **Metric cards**
   - Display the 9 calculated metrics as styled cards instead of raw JSON
   - Add market cap, 52-week high/low, volume

9. **News cards**
   - Format news articles as cards with title, source, time, thumbnail
   - Link to original article

10. **Market status indicator**
    - Detect if US market is open/closed
    - Show banner on dashboard and watchlist

### Phase 3: Make Watchlist Work

11. **Watchlist backend**
    - `POST /api/watchlist` — add stock
    - `DELETE /api/watchlist/{symbol}` — remove stock
    - `GET /api/watchlist` — list user's watchlist
    - MongoDB `watchlists` collection (user_id, symbols[])

12. **Watchlist frontend**
    - Stock cards with current price (from price API)
    - Add/remove buttons
    - Market status notice at bottom

13. **Add to watchlist from dashboard**
    - Button on dashboard search results to save stock

### Phase 4: Implement Real Research Engine

14. **Wire research engine to real data**
    - `financial_analysis.py` → use Alpha Vantage data to compute real ratios
    - `growth_analysis.py` → YoY growth from historical annual reports
    - `valuation.py` → PE, PB, DCF from real numbers
    - `risk_analysis.py` → leverage ratios, volatility if price data available

15. **LLM-powered report generation**
    - Feed real metrics + RAG context to Gemini
    - Generate structured narrative reports

16. **Wire intent detector**
    - Route queries to appropriate handlers (price → financial service, news → news service, etc.)
    - Or decide to keep unified search and remove dead code

### Phase 5: Knowledge Base Expansion

17. **SEC filing ingestion**
    - Implement SEC EDGAR API properly
    - Ingest 10-K, 10-Q filings
    - Chunk and embed into ChromaDB

18. **Earnings transcript ingestion**
    - Source transcripts (free APIs or scraping)
    - Process and embed

19. **Financial theory corpus**
    - Curate financial textbook content, investment frameworks
    - Embed as reference knowledge

20. **News ingestion into RAG**
    - Periodically ingest news articles into ChromaDB
    - Enable RAG to cite recent news

### Phase 6: Polish & Production

21. **Forgot password frontend** — wire to backend OTP flow
22. **Google OAuth** — implement OAuth flow
23. **Dashboard data caching** — cache search results until logout
24. **404 page**
25. **Proper logging** — replace all print statements
26. **Error messages** — user-friendly instead of raw exceptions
27. **Loading skeletons** — better UX than spinners

---

## What's Real vs What's Fake

A quick reference for what actually computes real data vs returns placeholders:

| Component | Real? |
|-----------|-------|
| Gemini LLM responses | ✅ Real (but ungrounded without RAG data) |
| Symbol resolution | ✅ Real |
| Alpha Vantage financial statements | ✅ Real |
| Financial metrics (9 ratios) | ✅ Real |
| NewsAPI articles | ✅ Real |
| Revenue/Profit chart | ✅ Real (from Alpha Vantage annual reports) |
| Auth system | ✅ Real |
| RAG retrieval | ❌ Empty (no documents in ChromaDB) |
| Research engine analysis | ❌ Placeholder text |
| SEC filings | ❌ Stub |
| Earnings transcripts | ❌ Stub |
| Stock prices | ❌ Not implemented |
| Watchlist | ❌ UI shell only |
| Conversation history | ❌ Saved but never loaded |

---

## Summary

**What works today**: You can log in, search a stock, get a Gemini AI answer (without RAG grounding), see Alpha Vantage financial statements + 9 calculated metrics + a revenue chart + news articles. You can chat with the AI. Dark/light theme works.

**The #1 gap**: The knowledge base is empty. RAG retrieval returns nothing. The AI answers from its own training data, not from curated financial intelligence. **Filling ChromaDB with financial knowledge is the single most impactful thing to do next.**

**The #2 gap**: No stock price data. Dashboard can't show a price chart, watchlist can't show current prices, and market status can't be determined.

**The #3 gap**: Research engine is all placeholders. The 9 metrics in `financial_metrics.py` are the only real calculations.
