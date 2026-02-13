"""News Loader"""

from mcp.news_api import news_api


class NewsLoader:
    async def load_news(self, symbol: str):
        articles = await news_api.fetch_news(symbol)
        return articles


news_loader = NewsLoader()
