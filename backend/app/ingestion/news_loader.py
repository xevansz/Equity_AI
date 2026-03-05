"""News Loader"""

from app.mcp.news_api import NewsAPI


class NewsLoader:
    def __init__(self, news_api: NewsAPI):
        self._news_api = news_api

    async def load_news(self, symbol: str):
        articles = await self._news_api.fetch_news(symbol)
        return articles


news_loader = NewsLoader(NewsAPI())
