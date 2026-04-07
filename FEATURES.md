# EquityAI — Features

> What's implemented, what's a stub, and what's left to build.

# Features left
3. **Chat** — Deep-dive conversational research powered by RAG + LLM

### 3. Chat (`/chat`)

**Goal**: Deep-dive financial research. RAG-powered conversational interface that retrieves from a knowledge base of financial theories, studies, SEC filings, reports, etc. The core product.

| Feature | Status | Details |
| --------- | -------- | --------- |
| **RAG retrieval from knowledge base** | ❌ Not working | ChromaDB is empty — no documents ingested. RAG pipeline runs but returns nothing, so Gemini answers without context |
| **Knowledge base ingestion** | ❌ Missing | No pipeline to ingest financial theories, studies, SEC filings, textbooks, etc. |
| **Source citations** | ❌ Missing | `sources: []` always returned empty |
| **Follow-up context** | ❌ Missing | Each message is independent — no conversation context sent to LLM |
| **Deep financial analysis** | ❌ Stubs | Research engine functions return placeholder text, not real analysis |

* Cursor should stay in the input bar even after sending the message.
* When viewing old chats search should persist

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
- ⚠️ PE Ratio always `None` (needs market price)
- These metrics are **the only real calculations** in the entire backend

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

4. **Source citations**
   - Track which documents were retrieved
   - Display sources in chat UI

### Phase 2: Make Dashboard Useful

1. **Stock price API**
- Add Twelve Data and Yahoo Finance (yfinance) as additional fallback providers - add as the primary providers
- Implement round-robin or priority-based provider rotation
- Backend endpoint: `GET /api/price/{symbol}?range=30d`

2. **Price chart component**
- Groww-style area chart with red (down) / green (up) coloring

3. **Market status indicator**
- Detect if US market is open/closed
- also, implement indian stocks
- Show banner on dashboard and watchlist

### Phase 3: Make Watchlist Work

1. **Watchlist frontend polish**
- Market status notice at bottom

### Phase 4: Implement Real Research Engine

1. **Wire research engine to real data**
    - `financial_analysis.py` → use Alpha Vantage data to compute real ratios
    - `growth_analysis.py` → YoY growth from historical annual reports
    - `valuation.py` → PE, PB, DCF from real numbers
    - `risk_analysis.py` → leverage ratios, volatility if price data available

2. **LLM-powered report generation**
    - Feed real metrics + RAG context to Gemini
    - Generate structured narrative reports

### Phase 5: Knowledge Base Expansion

1. **SEC filing ingestion**
    - Implement SEC EDGAR API properly
    - Ingest 10-K, 10-Q filings
    - Chunk and embed into ChromaDB

2. **Earnings transcript ingestion**
    - Source transcripts (free APIs or scraping)
    - Process and embed

3. **Financial theory corpus**
    - Curate financial textbook content, investment frameworks
    - Embed as reference knowledge

4. **News ingestion into RAG**
    - Periodically ingest news articles into ChromaDB
    - Enable RAG to cite recent news

### Phase 6: Polish & Production

5. **Loading skeletons** — better UX than spinners

## What's Fake

A quick reference for what actually computes real data vs returns placeholders:

| Component | Real? |
|-----------|-------|
| RAG retrieval | ❌ Empty (no documents in ChromaDB) |
| Research engine analysis | ❌ Placeholder text |
| SEC filings | ❌ Stub |
| Earnings transcripts | ⚠️ Retrieval exists, ingestion/embedding not done |

## Summary

**What works today**: You can log in, search a stock, get a Gemini AI answer (without RAG grounding), see Alpha Vantage financial statements + 9 calculated metrics + a revenue chart + news articles. You can chat with the AI. Dark/light theme works.

**The #1 gap**: The knowledge base is empty. RAG retrieval returns nothing. The AI answers from its own training data, not from curated financial intelligence. **Filling ChromaDB with financial knowledge is the single most impactful thing to do next.**

**The #2 gap**: The chat system still lacks grounded sources and follow-up conversational context, so answers are not yet citation-backed or multi-turn aware.

**The #3 gap**: Research engine is all placeholders. The 9 metrics in `financial_metrics.py` are the only real calculations.

Recommendations Priority

Fix infinite recursion in API key rotation
Remove hardcoded admin credentials
Initialize update_task variable in WebSocket handler
Add JWT secret validation at startup

Implement cache eviction in ChatService
Make SMTP operations async

Implement repository layer for database access

 
Implement connection pooling for external APIs