"""News API Connector"""

from app.mcp.base import BaseMCP
from app.config import settings


class NewsAPI(BaseMCP):
    def __init__(self):
        super().__init__("https://newsapi.org/v2", settings.NEWSAPI_KEY)

    async def fetch_news(self, symbol: str, limit: int = 10):
        if not self.api_key:
            return []
        try:
            data = await self.get(
                "everything",
                {
                    "q": symbol,
                    "language": "en",
                    "sortBy": "publishedAt",
                    "pageSize": limit,
                },
            )
            return data.get("articles", [])
        except Exception as e:
            print("Error fetching news:", e)
            return []


news_api = NewsAPI()
