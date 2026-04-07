"""Transcripts API"""

import re
from datetime import UTC, datetime

from fastapi import APIRouter, Depends, HTTPException, Path, Query
from motor.motor_asyncio import AsyncIOMotorDatabase

from app.dependencies import get_current_user, get_database, get_transcript_loader
from app.ingestion.transcript_loader import TranscriptLoader
from app.logging_config import get_logger

logger = get_logger(__name__)

router = APIRouter(prefix="/api", tags=["transcripts"])


def _current_quarter() -> tuple[int, int]:
    now = datetime.now(UTC)
    return now.year, (now.month - 1) // 3 + 1


@router.get("/transcripts/{symbol}")
async def get_transcript(
    symbol: str = Path(..., min_length=1, max_length=20, description="Stock symbol"),
    year: int | None = Query(None, ge=2000, le=2100, description="Year"),
    quarter: int | None = Query(None, ge=1, le=4, description="Quarter (1-4)"),
    user: dict = Depends(get_current_user),
    transcript_loader: TranscriptLoader = Depends(get_transcript_loader),
    db: AsyncIOMotorDatabase = Depends(get_database),
) -> dict:
    """Get the latest earnings call transcript for a symbol.

    Defaults to the current quarter. Supply `year` and `quarter` query params
    to request a specific period (e.g. ?year=2024&quarter=3).
    """
    symbol = symbol.strip().upper()
    if not re.match(r"^[A-Z0-9.\-:]+$", symbol):
        raise HTTPException(status_code=400, detail="Invalid symbol format")

    if year is None or quarter is None:
        year, quarter = _current_quarter()

    if quarter not in (1, 2, 3, 4):
        raise HTTPException(status_code=400, detail="quarter must be 1-4")

    try:
        logger.info("Transcript request: %s Q%d %d", symbol, quarter, year)
        doc = await transcript_loader.load_transcript(symbol, year, quarter, db=db)
        return doc.model_dump(exclude={"raw"})
    except HTTPException:
        raise
    except Exception as e:
        logger.exception("Transcript API error")
        raise HTTPException(status_code=500, detail=str(e)) from e
