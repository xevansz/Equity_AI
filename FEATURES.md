# EquityAI — Features

> What's implemented, what's a stub, and what's left to build.

# Features left
3. **Chat** — Deep-dive conversational research powered by RAG + LLM

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

3. **Source citations**
   - Track which documents were retrieved
   - Display sources in chat UI


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

## What's Fake

A quick reference for what actually computes real data vs returns placeholders:

| Component | Real? |
|-----------|-------|
| RAG retrieval | ❌ Empty (no documents in ChromaDB) |
| Research engine analysis | ❌ Placeholder text |
| SEC filings | ❌ Stub |
| Earnings transcripts | ⚠️ Retrieval exists, ingestion/embedding not done |

Implement repository layer for database access