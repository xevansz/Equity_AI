"""Cache Warmer — keeps ingested_documents warm for watchlisted symbols.

Runs as a background asyncio task started during FastAPI lifespan.
No extra dependencies required (pure asyncio + existing Motor client).
"""

import asyncio
from datetime import UTC, datetime

from motor.motor_asyncio import AsyncIOMotorDatabase

from app.ingestion.news_loader import NewsLoader
from app.ingestion.transcript_loader import TranscriptLoader
from app.logging_config import get_logger

logger = get_logger(__name__)

# How often to re-warm the cache (seconds)
NEWS_WARM_INTERVAL = 15 * 60  # 15 minutes
TRANSCRIPT_WARM_INTERVAL = 6 * 3600  # 6 hours


async def _warm_news(db: AsyncIOMotorDatabase, news_loader: NewsLoader) -> None:
    """Fetch and cache news for all symbols present in the watchlist."""
    try:
        symbols = await db.watchlist.distinct("symbol")
        if not symbols:
            return
        logger.info("Warmer: refreshing news for %d symbol(s)", len(symbols))
        for symbol in symbols:
            try:
                await news_loader.load_news(symbol, db=db)
            except Exception:
                logger.exception("Warmer: news refresh failed for %s", symbol)
    except Exception:
        logger.exception("Warmer: _warm_news encountered an unexpected error")


async def _warm_transcripts(db: AsyncIOMotorDatabase, transcript_loader: TranscriptLoader) -> None:
    """Pre-fetch transcripts for the current and previous quarter for all watchlisted symbols."""
    try:
        symbols = await db.watchlist.distinct("symbol")
        if not symbols:
            return

        now = datetime.now(UTC)
        current_quarter = (now.month - 1) // 3 + 1
        current_year = now.year
        # Also warm the previous quarter
        prev_quarter = current_quarter - 1 if current_quarter > 1 else 4
        prev_year = current_year if current_quarter > 1 else current_year - 1

        quarters_to_warm = [
            (current_year, current_quarter),
            (prev_year, prev_quarter),
        ]

        logger.info("Warmer: refreshing transcripts for %d symbol(s)", len(symbols))
        for symbol in symbols:
            for year, quarter in quarters_to_warm:
                try:
                    await transcript_loader.load_transcript(symbol, year, quarter, db=db)
                except Exception:
                    logger.exception("Warmer: transcript refresh failed for %s Q%d %d", symbol, quarter, year)
    except Exception:
        logger.exception("Warmer: _warm_transcripts encountered an unexpected error")


async def run_warmer(
    db: AsyncIOMotorDatabase,
    news_loader: NewsLoader,
    transcript_loader: TranscriptLoader,
) -> None:
    """
    Long-running asyncio task that periodically warms the Mongo cache.
    Start with: asyncio.create_task(run_warmer(...))
    """
    logger.info(
        "Ingestion cache warmer started (news=%ds, transcripts=%ds)", NEWS_WARM_INTERVAL, TRANSCRIPT_WARM_INTERVAL
    )

    news_countdown = 0
    transcript_countdown = 0

    while True:
        await asyncio.sleep(60)  # tick every minute
        news_countdown += 60
        transcript_countdown += 60

        if news_countdown >= NEWS_WARM_INTERVAL:
            news_countdown = 0
            await _warm_news(db, news_loader)

        if transcript_countdown >= TRANSCRIPT_WARM_INTERVAL:
            transcript_countdown = 0
            await _warm_transcripts(db, transcript_loader)
