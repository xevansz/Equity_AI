"""News API"""

from fastapi import APIRouter, HTTPException
from mcp.news_api import NewsAPI

router = APIRouter()


@router.get("/news/{symbol}")
async def get_news(symbol: str):
    """Get latest news for symbol"""
    try:
        print("\n📰 NEWS REQUEST:", symbol)
        news_api = NewsAPI()
        news = await news_api.fetch_news(symbol)
        print(f"🗞 {len(news)} News Articles Fetched")
        if len(news) > 0:
            print("Top headline:", news[0].get("title"))
        print("-" * 60)

        news_api = NewsAPI()
        news = await news_api.fetch_news(symbol)

        return {"symbol": symbol, "news": news}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
