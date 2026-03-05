"""News API"""

from fastapi import APIRouter, Depends, HTTPException

from app.dependencies import get_current_user, get_news_api
from app.logging_config import get_logger
from app.mcp.news_api import NewsAPI

logger = get_logger(__name__)

router = APIRouter(tags=["news"])


@router.get("/news/{symbol}")
async def get_news(
    symbol: str,
    user: dict = Depends(get_current_user),
    news_api: NewsAPI = Depends(get_news_api),
) -> dict:
    """Get latest news for symbol"""
    try:
        logger.info("News request: %s", symbol)
        news = await news_api.fetch_news(symbol)
        logger.info("News articles fetched: %s", len(news))
        if len(news) > 0:
            logger.debug("Top headline: %s", news[0].get("title"))

        return {"symbol": symbol, "news": news}
    except Exception as e:
        logger.exception("News API error")
        raise HTTPException(status_code=500, detail=str(e)) from e
