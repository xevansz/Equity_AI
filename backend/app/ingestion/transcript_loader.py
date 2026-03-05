"""Earnings Call Transcripts"""

import hashlib
import re
from abc import ABC, abstractmethod

from motor.motor_asyncio import AsyncIOMotorDatabase

from app.ingestion.data_cleaner import data_cleaner
from app.logging_config import get_logger
from app.mcp.base import BaseMCP
from app.schemas.ingestion import IngestionDocument

logger = get_logger(__name__)

COLLECTION = "ingested_documents"


def _make_transcript_id(symbol: str, year: int, quarter: int, source: str) -> str:
    key = f"{source}:{symbol.upper()}:{year}:Q{quarter}"
    return hashlib.sha256(key.encode()).hexdigest()[:24]


# Provider interface — swap implementations without touching the loader
class TranscriptProvider(ABC):
    @abstractmethod
    async def fetch(self, symbol: str, year: int, quarter: int) -> str | None:
        """Return plain-text transcript, or None if not available."""


class SECTranscriptProvider(TranscriptProvider):
    """
    Free best-effort provider using SEC EDGAR full-text search.
    Looks for 8-K filings (earnings call exhibits) for the given symbol/quarter.
    Returns None when nothing useful is found; the loader handles that gracefully.
    """

    _EDGAR_SEARCH = "https://efts.sec.gov/LATEST/search-index"
    _EDGAR_BASE = "https://www.sec.gov"

    def __init__(self):
        self._client = BaseMCP(self._EDGAR_BASE)

    async def fetch(self, symbol: str, year: int, quarter: int) -> str | None:
        try:
            return await self._search_edgar(symbol, year, quarter)
        except Exception:
            logger.exception("SEC transcript fetch failed for %s Q%d %d", symbol, quarter, year)
            return None

    async def _search_edgar(self, symbol: str, year: int, quarter: int) -> str | None:
        import httpx

        query = f"{symbol} earnings call transcript"
        params = {
            "q": f'"{query}"',
            "dateRange": "custom",
            "startdt": f"{year}-01-01",
            "enddt": f"{year}-12-31",
            "forms": "8-K",
        }
        async with httpx.AsyncClient(timeout=20.0) as client:
            resp = await client.get(
                "https://efts.sec.gov/LATEST/search-index",
                params=params,
                headers={"User-Agent": "EquityAI research@equityai.com"},
            )
            if resp.status_code != 200:
                return None
            data = resp.json()

        hits = (data.get("hits") or {}).get("hits") or []
        if not hits:
            return None

        # Take the first matching filing document
        filing = hits[0].get("_source") or {}

        # Try to fetch the actual text from the filing index
        accession = (filing.get("accession_no") or "").replace("-", "")
        cik = filing.get("entity_id") or ""
        if not accession or not cik:
            return None

        index_url = f"/Archives/edgar/data/{cik}/{accession}/{accession}-index.htm"
        async with httpx.AsyncClient(timeout=20.0) as client:
            idx_resp = await client.get(
                self._EDGAR_BASE + index_url,
                headers={"User-Agent": "EquityAI research@equityai.com"},
            )
            if idx_resp.status_code != 200:
                return None
            html = idx_resp.text

        # Find .txt exhibit links
        txt_links = re.findall(r'href="(/Archives/edgar/data/[^"]+\.txt)"', html, re.IGNORECASE)
        if not txt_links:
            return None

        async with httpx.AsyncClient(timeout=30.0) as client:
            doc_resp = await client.get(
                self._EDGAR_BASE + txt_links[0],
                headers={"User-Agent": "EquityAI research@equityai.com"},
            )
            if doc_resp.status_code != 200:
                return None
            raw_text = doc_resp.text

        # Strip HTML tags and normalize whitespace
        clean = re.sub(r"<[^>]+>", " ", raw_text)
        clean = data_cleaner.clean_text(clean)
        return clean if len(clean) > 200 else None


class NullTranscriptProvider(TranscriptProvider):
    """Fallback — returns None so the loader marks the doc as unavailable."""

    async def fetch(self, symbol: str, year: int, quarter: int) -> str | None:
        return None


class TranscriptLoader:
    def __init__(self, provider: TranscriptProvider | None = None):
        self._provider: TranscriptProvider = provider or SECTranscriptProvider()

    def set_provider(self, provider: TranscriptProvider) -> None:
        """Swap the transcript provider at runtime (e.g. to a paid one)."""
        self._provider = provider

    async def load_transcript(
        self,
        symbol: str,
        year: int,
        quarter: int,
        db: AsyncIOMotorDatabase | None = None,
    ) -> IngestionDocument:
        """
        Return a cached or freshly fetched transcript for symbol/year/quarter.
        - If a cached doc exists in Mongo it is returned immediately (fast path).
        - Otherwise the configured provider is called, the result cached, and returned.
        - When the provider returns nothing, a typed "not_available" doc is cached
          so we don't hammer the provider on every request.
        """
        doc_id = _make_transcript_id(symbol, year, quarter, self._provider.__class__.__name__)

        # Fast path: check Mongo cache first
        if db is not None:
            cached = await db[COLLECTION].find_one({"_id": doc_id})
            if cached is not None:
                return IngestionDocument.from_mongo(cached)

        # Slow path: fetch from provider
        text = await self._provider.fetch(symbol, year, quarter)
        available = bool(text and len(text.strip()) > 50)

        doc = IngestionDocument(
            id=doc_id,
            symbol=symbol.upper(),
            source=self._provider.__class__.__name__.lower().replace("transcriptprovider", ""),
            type="earnings_transcript",
            title=f"{symbol.upper()} Q{quarter} {year} Earnings Call"
            if available
            else f"{symbol.upper()} Q{quarter} {year} — Transcript Not Available",
            text=text or "",
            url="",
            published_at=f"{year}-01-01",
            raw={"year": year, "quarter": quarter, "available": available},
        )

        if db is not None:
            try:
                await db[COLLECTION].insert_one(doc.to_mongo())
                logger.info(
                    "Cached transcript for %s Q%d %d (available=%s)",
                    symbol,
                    quarter,
                    year,
                    available,
                )
            except Exception as e:
                logger.exception("Error %s", e)  # duplicate key on race condition — safe to ignore

        return doc


transcript_loader = TranscriptLoader()
