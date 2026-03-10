# EquityAI
An LLM-powered real-time knowledge curation system for financial intelligence.

## RAG System (`rag/`)

| Component                       | Status                                                          |
| ------------------------------- | --------------------------------------------------------------- |
| `query_expander.py`             | ⚠️ Dead code — kept as placeholder for future multi-query RAG   |
| `rag_pipeline.py`               | ✅ Wired — runs only for `research_query` / `general_query`     |
| `retriever.py`                  | ✅ Queries Chroma collection                                    |
| `context_builder.py`            | ✅ Builds context string from retrieved chunks                  |

### Ingestion Pipeline (`ingestion/`)

| Component                       | Status                                                          |
| ------------------------------- | --------------------------------------------------------------- |
| `news_loader.py`                | ✅ Fetches + caches news to Mongo (API-only, not embedded)      |
| `transcript_loader.py`          | ✅ Fetches + caches earnings transcripts to Mongo               |
| `sec_filing_loader.py`          | ✅ Fetches latest 10-K/10-Q from EDGAR, caches to Mongo         |
| `vector_ingestion_service.py`   | ✅ Chunks Mongo docs → upserts into Chroma with stable IDs      |
| `warmer.py`                     | ✅ Background Mongo cache warmer (news + transcripts)           |

### Admin Ingestion Endpoints

| Endpoint                        | Description                                                     |
| ------------------------------- | --------------------------------------------------------------- |
| `POST /api/admin/ingest/{sym}`  | Fetch transcripts + 10-K/10-Q → Mongo → embed into Chroma       |
| `POST /api/admin/reindex/{sym}` | Re-chunk + re-upsert from Mongo into Chroma (no re-fetch)       |

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
1. **Add nginx reverse proxy** with SSL
2. **Add API rate limiting** middleware (slowapi or similar)
3. **Explicit repo layer** isolate persistant logic from services  * ingestion may fetch apis
4. Build Explicit repo layer
    * Services(symbolcacheservice) directly calls monogdb
    * memory probably does DB ops
5. Add delete chat in conversations. chat page
