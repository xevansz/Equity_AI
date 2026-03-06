"""SEC Filings API — uses SEC EDGAR public REST endpoints (no API key required)."""

from app.config import settings
from app.logging_config import get_logger
from app.mcp.base import BaseMCP

logger = get_logger(__name__)

_SEC_USER_AGENT = settings.SEC_USER_AGENT

_FORM_PRIORITY = {"10-K", "10-Q", "8-K", "DEF 14A", "S-1", "20-F"}
_DEFAULT_LIMIT = 20


class SECAPI(BaseMCP):
    """SEC EDGAR connector.

    Resolves ticker → CIK via the SEC's bulk company_tickers.json, then
    fetches the submissions feed from data.sec.gov to return normalized
    recent filings.
    """

    # SEC public APIs are lightly rate-limited; cache aggressively.
    CACHE_TTL: float = 3600.0  # 1 hour for filings
    MAX_RETRIES: int = 3
    BACKOFF_BASE: float = 2.0

    _TICKERS_URL = "https://www.sec.gov/files/company_tickers.json"
    _SUBMISSIONS_BASE = "https://data.sec.gov/submissions"

    def __init__(self):
        # base_url is unused for SEC (different sub-domains per call); set to EDGAR root.
        super().__init__("https://www.sec.gov")
        self.client.headers.update(
            {
                "User-Agent": _SEC_USER_AGENT,
                "Accept-Encoding": "gzip, deflate",
                "Accept": "application/json",
            }
        )
        # separate long-lived cache for the ticker→CIK mapping
        self._ticker_map: dict[str, str] | None = None  # ticker_upper -> zero-padded CIK

    async def _fetch_json_url(self, url: str) -> object:
        """Low-level GET bypassing the endpoint-building in BaseMCP.get()
        so we can hit arbitrary SEC sub-domain URLs while still benefiting
        from the circuit breaker and retry logic."""
        import asyncio
        import random

        from app.mcp.base import CircuitOpenError

        cache_key = self._cache_key(url, {})
        cached = self._cache_get(cache_key)
        if cached is not None:
            return cached

        self._cb_check()

        last_exc = None
        for attempt in range(self.MAX_RETRIES + 1):
            try:
                response = await self.client.get(url)
                if response.status_code == 429 or response.status_code >= 500:
                    response.raise_for_status()
                response.raise_for_status()
                payload = response.json()
                self._cb_record_success()
                self._cache_set(cache_key, payload)
                return payload
            except CircuitOpenError:
                raise
            except Exception as exc:
                last_exc = exc
                self._cb_record_failure()
                if attempt == self.MAX_RETRIES:
                    break
                delay = min(
                    self.BACKOFF_BASE * (2**attempt) + random.uniform(0.0, 0.5),
                    self.BACKOFF_MAX,
                )
                await asyncio.sleep(delay)

        raise last_exc

    async def _get_ticker_map(self) -> dict[str, str]:
        """Return (and cache in-process) the full ticker → zero-padded CIK map."""
        if self._ticker_map is not None:
            return self._ticker_map

        data = await self._fetch_json_url(self._TICKERS_URL)
        mapping: dict[str, str] = {}
        for entry in data.values():
            ticker = str(entry.get("ticker", "")).upper()
            cik = str(entry.get("cik_str", "")).zfill(10)
            if ticker:
                mapping[ticker] = cik

        self._ticker_map = mapping
        return mapping

    @staticmethod
    def _build_filing_url(cik: str, accession: str, primary_doc: str) -> str:
        acc_nodash = accession.replace("-", "")
        return f"https://www.sec.gov/Archives/edgar/data/{int(cik)}/{acc_nodash}/{primary_doc}"

    @staticmethod
    def _normalize_filings(raw_recent: dict, cik: str, limit: int) -> list[dict]:
        """Convert the 'recent' block from the submissions feed into a flat list."""
        form_types = raw_recent.get("form", [])
        accessions = raw_recent.get("accessionNumber", [])
        filed_dates = raw_recent.get("filingDate", [])
        primary_docs = raw_recent.get("primaryDocument", [])
        descriptions = raw_recent.get("primaryDocDescription", [])

        filings: list[dict] = []
        for form, accession, date, doc, desc in zip(
            form_types, accessions, filed_dates, primary_docs, descriptions, strict=False
        ):
            if len(filings) >= limit:
                break
            url = SECAPI._build_filing_url(cik, accession, doc) if doc else ""
            filings.append(
                {
                    "form": form,
                    "accession_number": accession,
                    "filing_date": date,
                    "primary_document": doc,
                    "description": desc,
                    "url": url,
                }
            )
        return filings

    # public API
    async def get_filings(
        self,
        ticker: str,
        limit: int = _DEFAULT_LIMIT,
    ) -> dict:
        """Return recent SEC filings for *ticker*.

        Returns
        -------
        dict with keys:
          ticker    – upper-cased input ticker
          cik       – zero-padded 10-digit CIK (empty string if unknown)
          filings   – list of dicts (form, accession_number, filing_date,
                      primary_document, description, url)
          error     – present only if something went wrong
        """
        ticker = ticker.upper().strip()

        try:
            ticker_map = await self._get_ticker_map()
        except Exception as exc:
            logger.exception("SEC: failed to fetch ticker→CIK map for %s", ticker)
            return {"ticker": ticker, "cik": "", "filings": [], "error": str(exc)}

        cik = ticker_map.get(ticker)
        if not cik:
            logger.warning("SEC: unknown ticker %s", ticker)
            return {"ticker": ticker, "cik": "", "filings": [], "error": f"Unknown ticker: {ticker}"}

        submissions_url = f"{self._SUBMISSIONS_BASE}/CIK{cik}.json"
        try:
            data = await self._fetch_json_url(submissions_url)
        except Exception as exc:
            logger.exception("SEC: failed to fetch submissions for %s (CIK %s)", ticker, cik)
            return {"ticker": ticker, "cik": cik, "filings": [], "error": str(exc)}

        recent = data.get("filings", {}).get("recent", {})
        filings = self._normalize_filings(recent, cik, limit)

        logger.info("SEC: fetched %d filings for %s (CIK %s)", len(filings), ticker, cik)
        return {"ticker": ticker, "cik": cik, "filings": filings}
