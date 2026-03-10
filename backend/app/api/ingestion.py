"""Admin Ingestion API — trigger document ingestion and Chroma re-indexing."""

from datetime import UTC, datetime

from fastapi import APIRouter, Depends, HTTPException
from motor.motor_asyncio import AsyncIOMotorDatabase

from app.dependencies import (
    admin_only,
    get_database,
    get_sec_api,
    get_transcript_loader,
    get_vector_ingestion_service,
    get_vector_store,
)
from app.embeddings.vector_store import VectorStore
from app.ingestion.sec_filing_loader import SECFilingLoader
from app.ingestion.transcript_loader import TranscriptLoader
from app.ingestion.vector_ingestion_service import VectorIngestionService
from app.logging_config import get_logger
from app.mcp.sec_api import SECAPI

logger = get_logger(__name__)

router = APIRouter(prefix="/api/admin", tags=["admin-ingestion"])


def _current_and_prev_quarters() -> list[tuple[int, int]]:
    now = datetime.now(UTC)
    current_q = (now.month - 1) // 3 + 1
    current_y = now.year
    prev_q = current_q - 1 if current_q > 1 else 4
    prev_y = current_y if current_q > 1 else current_y - 1
    return [(current_y, current_q), (prev_y, prev_q)]


@router.post("/ingest/{symbol}")
async def ingest_symbol(
    symbol: str,
    db: AsyncIOMotorDatabase = Depends(get_database),
    _admin: dict = Depends(admin_only),
    transcript_loader: TranscriptLoader = Depends(get_transcript_loader),
    sec_api: SECAPI = Depends(get_sec_api),
    vector_store: VectorStore = Depends(get_vector_store),
    ingestion_service: VectorIngestionService = Depends(get_vector_ingestion_service),
) -> dict:
    """
    Fetch transcripts + latest 10-K/10-Q for *symbol* into MongoDB, then embed all
    ingested docs for that symbol into Chroma. Admin only.
    """
    symbol = symbol.upper()
    logger.info("Admin ingest triggered for %s", symbol)

    # 1) Warm transcripts (current + previous quarter)
    transcripts_cached = 0
    for year, quarter in _current_and_prev_quarters():
        try:
            doc = await transcript_loader.load_transcript(symbol, year, quarter, db=db)
            if doc.raw and doc.raw.get("available"):
                transcripts_cached += 1
        except Exception:
            logger.exception("Transcript load failed for %s Q%d %d", symbol, quarter, year)

    # 2) Fetch latest SEC filing (10-K or 10-Q)
    filing_cached = False
    try:
        filing_loader = SECFilingLoader(sec_api)
        filing_doc = await filing_loader.load_filing(symbol, db=db)
        if filing_doc and filing_doc.text:
            filing_cached = True
    except Exception:
        logger.exception("SEC filing load failed for %s", symbol)

    # 3) Embed all docs for this symbol into Chroma
    try:
        embed_result = await ingestion_service.ingest(symbol, db, vector_store)
    except Exception as e:
        logger.exception("Vector ingestion failed for %s", symbol)
        raise HTTPException(status_code=500, detail=f"Embedding step failed: {e}") from e

    return {
        "symbol": symbol,
        "transcripts_cached": transcripts_cached,
        "filing_cached": filing_cached,
        "docs_embedded": embed_result["docs_embedded"],
        "chunks_embedded": embed_result["chunks_embedded"],
    }


@router.post("/reindex/{symbol}")
async def reindex_symbol(
    symbol: str,
    db: AsyncIOMotorDatabase = Depends(get_database),
    _admin: dict = Depends(admin_only),
    vector_store: VectorStore = Depends(get_vector_store),
    ingestion_service: VectorIngestionService = Depends(get_vector_ingestion_service),
) -> dict:
    """
    Re-chunk and re-upsert all cached docs for *symbol* into Chroma from MongoDB.
    Does not re-fetch from external APIs. Admin only.
    """
    symbol = symbol.upper()
    logger.info("Admin reindex triggered for %s", symbol)

    try:
        result = await ingestion_service.reindex(symbol, db, vector_store)
    except Exception as e:
        logger.exception("Reindex failed for %s", symbol)
        raise HTTPException(status_code=500, detail=str(e)) from e

    return {"symbol": symbol, **result}
