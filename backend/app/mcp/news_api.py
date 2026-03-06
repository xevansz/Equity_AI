"""News API Connector"""

from app.config import settings
from app.logging_config import get_logger
from app.mcp.base import BaseMCP

logger = get_logger(__name__)


class NewsAPI(BaseMCP):
    CACHE_TTL: float = 60.0  # 1 min — news is time-sensitive

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
            logger.exception("Error fetching news: %s", str(e))
            return []
