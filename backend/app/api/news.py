"""News API"""

from fastapi import APIRouter, Depends, HTTPException

from app.dependencies import get_current_user
from app.mcp.news_api import NewsAPI

router = APIRouter(tags=["news"])


@router.get("/news/{symbol}")
async def get_news(symbol: str, user: dict = Depends(get_current_user)) -> dict:
    """Get latest news for symbol"""
    try:
        print("\nNEWS REQUEST:", symbol)
        news_api = NewsAPI()
        news = await news_api.fetch_news(symbol)
        print(f"{len(news)} News Articles Fetched")
        if len(news) > 0:
            print("Top headline:", news[0].get("title"))
        print("-" * 60)

        return {"symbol": symbol, "news": news}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e)) from e
