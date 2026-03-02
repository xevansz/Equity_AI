# Global State: Watchlist + Search Results

Add global state for watchlist (MongoDB-persisted) and search results (localStorage-persisted), wire an "Add to Watchlist" button in the dashboard, and rebuild the watchlist page as a card grid with live prices.

---

## Backend

### 1. `backend/app/models/watchlist.py`
New Pydantic model:
```python
WatchlistItem(symbol, name, user_id, added_at)
```

### 2. `backend/app/api/watchlist.py`
Three endpoints (all require JWT auth, scoped to `user_id` from token):
- `GET /api/watchlist` — return all items for current user
- `POST /api/watchlist` — add `{ symbol, name }` (duplicate guard)
- `DELETE /api/watchlist/{symbol}` — remove by symbol

### 3. `backend/app/main.py`
Register new router: `app.include_router(watchlist.router, prefix="/api", tags=["watchlist"])`

---

## Frontend

### 4. `src/api/watchlist.js`
Three functions wrapping axios calls to the endpoints above:
`fetchWatchlist()`, `addToWatchlist(symbol, name)`, `removeFromWatchlist(symbol)`

### 5. `src/context/WatchlistContext.jsx`
- State: `items[]`, `loading`, `error`
- Actions: `fetchWatchlist()` (called on mount/login), `add(symbol, name)`, `remove(symbol)`
- Backed by the backend API

### 6. `src/context/SearchContext.jsx`
- State: `query`, `results`, `loading`, `error`
- `results` persisted to `localStorage` under key `eq_search_results`
- `runSearch(query)` calls `/api/search` and saves result
- Exposes `clearResults()` (called on logout)

### 7. `src/main.jsx`
Wrap app with `<SearchProvider>` and `<WatchlistProvider>` inside `<AuthProvider>`.

### 8. `src/pages/DashboardPage.jsx`
- Replace local `useSearch()` hook with `useContext(SearchContext)`
- After results load, show **"+ Add to Watchlist"** button (uses `data.symbol` + `data.query` as name)
- Button disabled / shows "✓ Added" if symbol already in watchlist

### 9. `src/components/Watchlist.jsx` + `src/pages/WatchlistPage.jsx`
- **Remove search bar** from WatchlistPage entirely
- `Watchlist` component reads from `WatchlistContext`
- Each card shows: **symbol**, **company name**, **current price** (fetched via `/api/financial` on mount), **Remove** button
- Loading skeleton while prices are fetching

### 10. `src/context/AuthContext.jsx`
- In `logout()`, call `clearResults()` from `SearchContext` to wipe `localStorage` key

---

## File change summary

| File | Action |
|---|---|
| `backend/app/models/watchlist.py` | **Create** |
| `backend/app/api/watchlist.py` | **Create** |
| `backend/app/main.py` | **Edit** — add import + router registration |
| `frontend/src/api/watchlist.js` | **Create** |
| `frontend/src/context/WatchlistContext.jsx` | **Create** |
| `frontend/src/context/SearchContext.jsx` | **Create** |
| `frontend/src/hooks/useSearch.js` | **No change** (kept, still used internally by SearchContext) |
| `frontend/src/main.jsx` | **Edit** — add providers |
| `frontend/src/pages/DashboardPage.jsx` | **Edit** — use SearchContext + Add to Watchlist button |
| `frontend/src/components/AnalysisPanel.jsx` | **Edit** — accept + render the Add to Watchlist button |
| `frontend/src/components/Watchlist.jsx` | **Edit** — consume WatchlistContext, card layout with price |
| `frontend/src/pages/WatchlistPage.jsx` | **Edit** — remove search bar |
| `frontend/src/context/AuthContext.jsx` | **Edit** — clear search results on logout |
