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
