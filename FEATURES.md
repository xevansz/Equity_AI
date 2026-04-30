# EquityAI — Features

## ❌ Broken / Incomplete Features

### Chat — RAG
| Feature | Status | Details |
|---------|--------|---------|
| **RAG retrieval from knowledge base** | ❌ Not working | ChromaDB collection is empty — admin ingest has never been run. RAG pipeline runs but returns nothing; Gemini answers without grounding |
| **Source citations** | ❌ Missing | `ChatResponse.sources` always returns `[]` — retrieved chunk metadata is never threaded back through `rag_pipeline → chat_service → response` |
| **Financial theory corpus** | ❌ Missing | No pipeline to ingest textbooks, frameworks, or reference PDFs |

### Chat — UI
| Feature | Status | Details |
|---------|--------|---------|
| **Cursor focus after send** | ❌ Missing | Input loses focus after sending; `inputRef.current?.focus()` not called in `handleSend` in `ConversationalChat.jsx` |
| **Search persistence on old chats** | ❌ Missing | Sidebar session search/filter not implemented; sessions are listed but not filterable |

### Research Engine
| Feature | Status | Details |
|---------|--------|---------|
| **`financial_analysis.py`** | ❌ Stub | `analyze_financials()` returns static bullet template — `FinancialAnalyzer` class exists but never called |
| **`growth_analysis.py`** | ❌ Stub | `analyze_growth()` returns static bullet template — `GrowthAnalyzer` class exists but never called |
| **`valuation_engine.py`** | ❌ Stub | `analyze_valuation()` returns static bullet template — `ValuationEngine.calculate_pe_ratio()` / `dcf_valuation()` exist but never called |
| **`risk_analysis.py`** | ❌ Stub | `analyze_risks()` returns static bullet template — `RiskAnalyzer` class exists but never called |
| **`report_generator.py` (sync)** | ❌ Bug | `generate_equity_report(symbol)` is called in `research.py` with two args `(req.symbol, db)` but function only accepts one |
| **LLM narrative report** | ⚠️ Partial | `ReportGenerator.generate_report()` class exists and calls Gemini, but `generate_equity_report()` never invokes it |

### News Ingestion into RAG
| Feature | Status | Details |
|---------|--------|---------|
| **News embedded into Chroma** | ❌ Missing | News articles saved to MongoDB but `VectorIngestionService` only ingests `earnings_transcript` and `sec_filing` types — `news_article` is excluded |

---

## 🔧 Features To Build — Prioritized

### Phase 1: Populate ChromaDB (Unblock RAG)

1. **Run admin ingest for key symbols**
   - Call `POST /api/admin/ingest/{symbol}` for symbols in watchlist
   - This will pull transcripts + SEC filings → chunk → embed into Chroma
   - Once Chroma has documents, RAG retrieval will return real context

2. **Add `news_article` to ingestible doc types**
   - Add `"news_article"` to `_DEFAULT_DOC_TYPES` in `vector_ingestion_service.py`
   - News is already in MongoDB; this just gates it from being embedded

3. **Surface source citations in chat**
   - Modify `retriever.py` to also return metadata (chunk source, title, URL)
   - Thread metadata through `rag_pipeline.run()` → `chat_service` → `ChatResponse.sources`

### Phase 2: Chat UI Fixes

1. **Keep cursor in input after send**
   - Add `inputRef` and call `inputRef.current?.focus()` after `setLoading(false)` in `ConversationalChat.jsx`

2. **Session search/filter in sidebar**
   - Add a search input above the session list in `ChatPage.jsx`
   - Filter `sessions` array by `last_message` content client-side

### Phase 3: Fix Research Engine

1. **Fix `generate_equity_report` call signature bug**
   - `research.py` calls `generate_equity_report(req.symbol, db)` but function only takes `symbol`
   - Remove the `db` argument from the call in `research.py`

2. **Wire class-based analyzers to real Alpha Vantage data**
   - `FinancialAnalyzer.analyze_liquidity/solvency` → use balance sheet from `financial_loader.py`
   - `GrowthAnalyzer.analyze_revenue_growth/earnings_growth` → use income statements
   - `ValuationEngine.calculate_pe_ratio/dcf_valuation` → use real price + earnings
   - `RiskAnalyzer.assess_market_risk` → use price history for beta/volatility

3. **Connect `ReportGenerator` (LLM narrative) to real data**
   - Replace `generate_equity_report()` with async `ReportGenerator.generate_report()` fed real metrics

### Phase 4: Knowledge Base Expansion

1. **Financial theory corpus**
   - Curate investment framework PDFs / textbook excerpts
   - Add a loader for local PDF/text files and ingest via `VectorIngestionService`

2. **Periodic full re-embed of news**
   - Extend `warmer.py` to call `ingestion_service.ingest(symbol, db, vector_store, doc_types=["news_article"])` periodically

---

## Fake 
| RAG retrieval | ❌ Empty | ChromaDB has no documents — ingest never triggered |
| Research engine analysis | ❌ Placeholder | All 4 `analyze_*()` functions return static strings |
| Source citations | ❌ Hardcoded | Always `[]` |