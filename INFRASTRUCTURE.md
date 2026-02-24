# EquityAI — Infrastructure

> What's built, what's wired, and what's missing in the system plumbing.

---

## Tech Stack

| Layer                  | Technology                                 | Status                                  |
| ---------------------- | ------------------------------------------ | --------------------------------------- |
| **Backend Framework**  | FastAPI (Python 3.12)                      | ✅ Running                              |
| **Package Manager**    | PDM (`pyproject.toml`)                     | ✅ Configured                           |
| **Database**           | MongoDB via Motor (async)                  | ✅ Connected                            |
| **Vector Store**       | ChromaDB (persistent)                      | ✅ Initialized                          |
| **LLM**                | Google Gemini 2.5 Flash (`google-genai`)   | ✅ Working                              |
| **Embeddings**         | `sentence-transformers` (all-MiniLM-L6-v2) | ⚠️ Code exists, not wired into pipeline |
| **Frontend Framework** | React 18 + Vite                            | ✅ Running                              |
| **Styling**            | TailwindCSS + CSS variables (dark/light)   | ✅ Working                              |
| **Routing**            | React Router v6                            | ✅ Working                              |
| **HTTP Client**        | Axios (with Vite proxy to backend)         | ✅ Working                              |
| **Charts**             | Recharts                                   | ✅ Installed, basic usage               |
| **Icons**              | Lucide React                               | ✅ Working                              |
| **Auth**               | JWT (python-jose) + bcrypt                 | ✅ Working                              |
| **Containerization**   | Docker Compose (backend + MongoDB)         | ⚠️ Partial                              |

---

## Backend Infrastructure

### App Lifecycle (`main.py`)

- ✅ FastAPI lifespan: connects MongoDB on startup, disconnects on shutdown
- ✅ Creates `symbol_cache` index on startup
- ✅ CORS configured for `localhost:3000`
- ✅ Global exception handler returns JSON 500s
- ✅ Root route serves built frontend or redirects to Vite dev server
- ✅ 6 API routers registered under `/api`

### Configuration (`config.py`)

- ✅ Pydantic `BaseSettings` with `.env` support
- ✅ All API keys, DB URIs, JWT config externalized
- ⚠️ JWT secret has a hardcoded default — should require env var
- ⚠️ `ADMIN_EMAIL` / `ADMIN_PASSWORD` have no defaults — app crashes if missing from `.env`

### Database (`database.py`)

- ✅ Singleton `Database` class with async connect/close
- ✅ Motor async client
- ✅ Index on `symbol_cache.company_name`
- ❌ No connection health check (just prints "connected" without verifying)
- ❌ No indexes on `conversations` or `users` collections

### Dependencies (`dependencies.py`)

- ✅ `get_database()` — returns MongoDB instance
- ✅ `get_current_user()` — extracts JWT from Bearer header
- ✅ `admin_only()` — role-based guard
- Clean dependency injection pattern throughout

### External API Connectors (`mcp/`)

| Connector            | File               | Status                                                     |
| -------------------- | ------------------ | ---------------------------------------------------------- |
| **Base HTTP client** | `base.py`          | ✅ Working — `httpx.AsyncClient` with 30s timeout          |
| **Alpha Vantage**    | `financial_api.py` | ✅ Working — income statement, balance sheet, cash flow    |
| **NewsAPI**          | `news_api.py`      | ✅ Working — fetches articles, graceful fallback if no key |
| **SEC EDGAR**        | `sec_api.py`       | ❌ Stub — returns empty `{"filings": []}`                  |

- ❌ `BaseMCP.client` (httpx) is **never closed** — resource leak
- ❌ No retry logic, no backoff, no circuit breaker
- ❌ No response caching — every search hits Alpha Vantage (5 calls/min free tier)

### Data Ingestion (`ingestion/`)

| Loader                 | Status                                         |
| ---------------------- | ---------------------------------------------- |
| `financial_loader.py`  | ✅ Calls Alpha Vantage for 3 statement types   |
| `data_cleaner.py`      | ✅ Basic text/dict cleaning utilities          |
| `news_loader.py`       | ⚠️ Thin wrapper over `news_api`, no processing |
| `transcript_loader.py` | ❌ Stub — returns empty string                 |

### Embeddings & Vector Store (`embeddings/`)

| Component         | Status                                                                                                      |
| ----------------- | ----------------------------------------------------------------------------------------------------------- |
| `vector_store.py` | ✅ ChromaDB persistent client, `add_documents()` and `search()` work                                        |
| `embedder.py`     | ⚠️ Code exists with lazy loading, but **import path is wrong** (`from config` instead of `from app.config`) |
| `chunker.py`      | ✅ Word-based chunking with overlap                                                                         |

- ❌ **No ingestion pipeline feeds documents into ChromaDB** — the vector store is empty
- ❌ Embedder is broken due to import error and is never called anywhere

### RAG System (`rag/`)

| Component            | Status                                                 |
| -------------------- | ------------------------------------------------------ |
| `rag_pipeline.py`    | ✅ Orchestrates retriever → context_builder            |
| `retriever.py`       | ✅ Queries ChromaDB vector store                       |
| `context_builder.py` | ✅ Concatenates documents into numbered context string |
| `query_expander.py`  | ⚠️ Exists but **never called** by the pipeline         |

- ❌ **RAG returns empty results** because ChromaDB has no documents ingested
- The pipeline structure is correct, but it has nothing to retrieve from

### LLM Layer (`llm/`)

| Component             | Status                                             |
| --------------------- | -------------------------------------------------- |
| `gemini.py`           | ✅ Async Gemini client, working                    |
| `symbol_resolver.py`  | ✅ LLM-powered company→ticker with MongoDB caching |
| `prompt_templates.py` | ✅ Two templates (financial analysis + chat)       |
| `response_parser.py`  | ⚠️ Exists but never used anywhere                  |

### Conversational Layer (`conversational/`)

| Component               | Status                                                                                   |
| ----------------------- | ---------------------------------------------------------------------------------------- |
| `memory.py`             | ✅ Saves/retrieves messages from MongoDB `conversations` collection                      |
| `response_generator.py` | ✅ Formats prompt and calls Gemini                                                       |
| `intent_detector.py`    | ⚠️ Keyword-based detection exists but **never called** in the actual flow                |
| `query_router.py`       | ⚠️ Maps intents to services but **never called** — all queries go through unified search |

- The intent detector and query router are wired to each other but disconnected from the actual request flow

### Services (`services/`)

| Service                   | Status                                                                                     |
| ------------------------- | ------------------------------------------------------------------------------------------ |
| `chat_service.py`         | ✅ Core chat: RAG → Gemini → cache → save to MongoDB                                       |
| `data_service.py`         | ✅ Loads financials, cleans rate-limit responses, calculates metrics                       |
| `financial_metrics.py`    | ✅ Calculates 9 metrics (Revenue, EPS, ROE, ROA, etc.) — PE ratio needs market price       |
| `symbol_cache_service.py` | ✅ MongoDB cache with aliases, use counts, timestamps                                      |
| `research_service.py`     | ⚠️ Exists but **never called** — `api/research.py` calls `generate_equity_report` directly |

### Authentication (`auth/`)

| Component           | Status                                                                                    |
| ------------------- | ----------------------------------------------------------------------------------------- |
| `auth_router.py`    | ✅ Register, login, forgot-password, reset-password, /me                                  |
| `jwt_handler.py`    | ✅ Create/verify JWT with HS256                                                           |
| `password_utils.py` | ✅ SHA256 pre-hash + bcrypt, password validation rules                                    |
| `user_service.py`   | ✅ CRUD for users collection                                                              |
| `smtp_service.py`   | ⚠️ Code works but **crashes on import** if SMTP env vars are missing (uses `require_env`) |
| `schemas.py`        | ✅ Pydantic models for auth requests                                                      |

- ⚠️ OTP store is **in-memory dict** — lost on restart, doesn't scale
- ⚠️ `ForgotPasswordRequest` schema requires `otp` field, but the forgot-password endpoint generates the OTP — schema mismatch
- ✅ Admin bypass via env vars works

### Schemas & Models

| Directory  | Purpose                          | Status                                                         |
| ---------- | -------------------------------- | -------------------------------------------------------------- |
| `schemas/` | Pydantic request/response models | ✅ chat, financial, research, user                             |
| `models/`  | Data models                      | ✅ conversation, company, financials, news, symbol_cache, user |

- Models are defined but most are **not used** — raw dicts are passed around instead

---

## Frontend Infrastructure

### Build & Dev (`vite.config.js`)

- ✅ Vite dev server on port 3000
- ✅ Proxy `/api` → `localhost:8000` (no CORS issues in dev)
- ✅ Source maps enabled for production builds

### Theming (`index.css` + `tailwind.config.js`)

- ✅ CSS custom properties for light/dark themes
- ✅ Tailwind maps to CSS variables (`bg-background`, `text-text`, etc.)
- ✅ `darkMode: 'class'` — toggled via `ThemeContext`
- ✅ Theme persisted in localStorage

### Auth Flow

- ✅ `AuthContext` — stores user + token, auto-validates on mount via `/api/auth/me`
- ✅ `ProtectedRoute` — redirects to `/login` if not authenticated
- ✅ Token stored in localStorage, set as Axios default header
- ✅ Login/Register with client-side validation

### API Layer (`api/`)

- ✅ `auth.js` — login, register, me
- ✅ `search.js` — unified search endpoint
- ❌ No dedicated API functions for financial, news, research, or watchlist endpoints

### State Management

- ✅ `AuthContext` — user auth state
- ✅ `ThemeContext` — light/dark toggle
- ❌ No global state for watchlist, search results, or dashboard data

---

## Deployment Infrastructure

### Docker Compose

- ✅ Backend service (port 8000)
- ✅ MongoDB service (port 27017) with persistent volume
- ❌ No frontend service
- ❌ No Dockerfile in backend directory (referenced but not present)
- ❌ No nginx/reverse proxy
- ❌ No SSL/TLS
- ❌ No ChromaDB volume mapping
- ❌ Missing most env vars (only MONGODB_URI and GEMINI_API_KEY passed)

### Dependency Management

- **Backend**: PDM (`pyproject.toml`) + separate `requirements.txt` with different packages
  - ⚠️ `pyproject.toml` and `requirements.txt` list **different dependencies** — confusing
  - `pyproject.toml`: fastapi, motor, chromadb, python-jose, google-genai + linters
  - `requirements.txt`: sentence-transformers, pymongo, yfinance, beautifulsoup4, lxml
  - Neither file includes: httpx, bcrypt, pydantic-settings, python-dotenv (all used in code)
- **Frontend**: npm (`package.json`) — ✅ clean and complete

---

## Known Bugs & Issues

1. **`embedder.py` broken import**: `from config import settings` should be `from app.config import settings`
2. **`smtp_service.py` crashes on import** if SMTP env vars aren't set — blocks entire app startup
3. **`health.py` has a bug**: `datetime.now(datetime.timezone(UTC))` — should be `datetime.now(UTC)`
4. **`BaseMCP` httpx client never closed** — connection/resource leak
5. **`ForgotPasswordRequest` schema** requires `otp` field but the endpoint generates it
6. **`vector_store.py` ID collision**: `add_documents()` always generates `doc_0, doc_1...` — overwrites on every call
7. **`financial_data.dict()`** in `search.py` — Pydantic v2 uses `.model_dump()`, not `.dict()`
8. **Inconsistent dependencies**: `pyproject.toml` vs `requirements.txt` list different packages; many used packages are in neither

---

## What Needs to Be Done (Infrastructure Only)

### Critical

1. **Fix `embedder.py` import** — broken, can't generate embeddings
2. **Fix `smtp_service.py`** — make SMTP optional so app doesn't crash without it
3. **Fix `health.py` datetime bug**
4. **Consolidate dependencies** — one source of truth, include all actually-used packages
5. **Build a document ingestion pipeline** — without this, RAG has nothing to retrieve
6. **Close httpx clients** on shutdown

### Important

7. **Add MongoDB connection health check** — verify connection actually works
8. **Add indexes** on `conversations.session_id` and `users.email`
9. **Replace print statements with `logging`** — structured logging throughout
10. **Fix vector store ID generation** — use content hashes or UUIDs
11. **Move OTP store to MongoDB** — in-memory dict doesn't survive restarts
12. **Wire intent detector + query router** into the actual request flow, or remove dead code
13. **Use Pydantic models consistently** — stop passing raw dicts

### Basics

14. **Add Dockerfile** for backend (Optional, not needed right now)
15. **Add frontend to docker-compose**
16. **Add nginx reverse proxy** with SSL
17. **Add Redis** for caching API responses and rate limiting
18. **Add API rate limiting** middleware (slowapi or similar)
19. **Encry password** password stored as a plain text right now
