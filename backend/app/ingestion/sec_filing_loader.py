"""SEC Filing Loader — fetches latest 10-K / 10-Q text from EDGAR and caches to Mongo."""

import hashlib
import re

import httpx
from motor.motor_asyncio import AsyncIOMotorDatabase

from app.ingestion.data_cleaner import data_cleaner
from app.logging_config import get_logger
from app.mcp.sec_api import SECAPI
from app.schemas.ingestion import IngestionDocument

logger = get_logger(__name__)

COLLECTION = "ingested_documents"
_FORM_PRIORITY = ["10-K", "10-Q"]
_SEC_BASE = "https://www.sec.gov"
_USER_AGENT = "EquityAI research@equityai.com"


def _make_filing_id(symbol: str, accession_no: str) -> str:
    key = f"sec:{symbol.upper()}:{accession_no}"
    return hashlib.sha256(key.encode()).hexdigest()[:24]


def _strip_html(html: str) -> str:
    text = re.sub(r"<[^>]+>", " ", html)
    text = re.sub(r"&[a-zA-Z]+;", " ", text)
    return data_cleaner.clean_text(text)


async def _fetch_filing_text(url: str) -> str | None:
    try:
        async with httpx.AsyncClient(timeout=30.0) as client:
            resp = await client.get(url, headers={"User-Agent": _USER_AGENT})
            if resp.status_code != 200:
                return None
            raw = resp.text
            clean = _strip_html(raw)
            return clean if len(clean) > 200 else None
    except Exception:
        logger.exception("Failed to fetch filing text from %s", url)
        return None


class SECFilingLoader:
    def __init__(self, sec_api: SECAPI):
        self._sec_api = sec_api

    async def load_filing(
        self,
        symbol: str,
        form_types: list[str] | None = None,
        db: AsyncIOMotorDatabase | None = None,
    ) -> IngestionDocument | None:
        """
        Fetch and cache the most recent 10-K or 10-Q for *symbol*.

        - Returns cached Mongo doc if already ingested.
        - Returns None if EDGAR has no matching filing or fetch fails.
        """
        form_types = form_types or _FORM_PRIORITY

        result = await self._sec_api.get_filings(symbol, limit=40)
        if result.get("error") or not result.get("filings"):
            logger.warning("SEC: no filings found for %s: %s", symbol, result.get("error"))
            return None

        # Pick the most recent filing matching the requested form types
        target = None
        for filing in result["filings"]:
            if filing.get("form") in form_types and filing.get("url"):
                target = filing
                break

        if target is None:
            logger.warning("SEC: no %s filing found for %s", "/".join(form_types), symbol)
            return None

        accession_no = target["accession_number"]
        doc_id = _make_filing_id(symbol, accession_no)

        # Fast path: return cached doc
        if db is not None:
            cached = await db[COLLECTION].find_one({"_id": doc_id})
            if cached is not None:
                logger.info("SEC: returning cached filing %s for %s", accession_no, symbol)
                return IngestionDocument.from_mongo(cached)

        # Slow path: fetch document text
        text = await _fetch_filing_text(target["url"])
        available = bool(text)

        doc = IngestionDocument(
            id=doc_id,
            symbol=symbol.upper(),
            source="sec_edgar",
            type="sec_filing",
            title=f"{symbol.upper()} {target['form']} — {target['filing_date']}",
            text=text or "",
            url=target["url"],
            published_at=target.get("filing_date", ""),
            raw={
                "form": target["form"],
                "accession_number": accession_no,
                "available": available,
            },
        )

        if db is not None:
            try:
                await db[COLLECTION].insert_one(doc.to_mongo())
                logger.info(
                    "SEC: cached %s filing for %s (accession=%s, available=%s)",
                    target["form"],
                    symbol,
                    accession_no,
                    available,
                )
            except Exception:
                logger.exception("SEC: failed to cache filing for %s", symbol)

        return doc
