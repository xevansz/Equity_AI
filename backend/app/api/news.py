"""News API"""

from fastapi import APIRouter, Depends, HTTPException
from motor.motor_asyncio import AsyncIOMotorDatabase

from app.dependencies import get_current_user, get_database, get_news_loader
from app.ingestion.news_loader import NewsLoader
from app.logging_config import get_logger

logger = get_logger(__name__)

router = APIRouter(prefix="/api", tags=["news"])


@router.get("/news/{symbol}")
async def get_news(
    symbol: str,
    user: dict = Depends(get_current_user),
    news_loader: NewsLoader = Depends(get_news_loader),
    db: AsyncIOMotorDatabase = Depends(get_database),
) -> dict:
    """Get latest normalized news for symbol"""
    try:
        logger.info("News request: %s", symbol)
        docs = await news_loader.load_news(symbol, db=db)
        logger.info("News articles fetched: %s", len(docs))
        if docs:
            logger.debug("Top headline: %s", docs[0].title)
        return {"symbol": symbol.upper(), "news": [d.model_dump(exclude={"raw"}) for d in docs]}
    except Exception as e:
        logger.exception("News API error")
        raise HTTPException(status_code=500, detail=str(e)) from e
