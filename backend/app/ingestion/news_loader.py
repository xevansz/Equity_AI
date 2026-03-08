"""News Loader"""

import hashlib

from motor.motor_asyncio import AsyncIOMotorDatabase

from app.ingestion.data_cleaner import data_cleaner
from app.logging_config import get_logger
from app.mcp.news_api import NewsAPI
from app.schemas.ingestion import IngestionDocument

logger = get_logger(__name__)

COLLECTION = "ingested_documents"


def _make_id(source: str, url: str) -> str:
    return hashlib.sha256(f"{source}:{url}".encode()).hexdigest()[:24]


def _normalize_article(symbol: str, article: dict) -> IngestionDocument | None:
    url = article.get("url") or ""
    title = article.get("title") or ""
    description = article.get("description") or ""
    content = article.get("content") or ""

    text = data_cleaner.clean_text(" ".join(filter(None, [title, description, content])))
    if not text:
        return None

    published_at = article.get("publishedAt") or ""

    return IngestionDocument(
        id=_make_id("newsapi", url),
        symbol=symbol.upper(),
        source="newsapi",
        type="news_article",
        title=data_cleaner.clean_text(title),
        text=text,
        url=url,
        published_at=published_at,
        raw=article,
    )


class NewsLoader:
    def __init__(self, news_api: NewsAPI):
        self._news_api = news_api

    async def load_news(self, symbol: str, db: AsyncIOMotorDatabase | None = None) -> list[IngestionDocument]:
        """
        Fetch and normalize news for `symbol`.
        - If `db` is provided, new articles are persisted to Mongo and only new ones are returned
          merged with any cached ones (so the response is always the full set).
        - If `db` is None, articles are fetched fresh and normalized without caching.
        """
        raw_articles = await self._news_api.fetch_news(symbol)
        normalized = [doc for a in raw_articles if (doc := _normalize_article(symbol, a))]

        if db is None or not normalized:
            return normalized

        collection = db[COLLECTION]

        # Upsert new docs (insert if not already present)
        new_ids = [doc.id for doc in normalized]

        if not new_ids:
            existing_ids = set()
        else:
            existing_ids = {
                d["_id"]
                async for d in collection.find(
                    {"_id": {"$in": new_ids}},
                    {"_id": 1},
                )
            }

        to_insert = [doc for doc in normalized if doc.id not in existing_ids]
        if to_insert:
            await collection.insert_many([doc.to_mongo() for doc in to_insert])
            logger.info("Ingested %d new news articles for %s", len(to_insert), symbol)

        # Return full cached set for this symbol (newest first)
        cached = [
            IngestionDocument.from_mongo(d)
            async for d in collection.find(
                {"symbol": symbol.upper(), "type": "news_article"},
            )
            .sort("published_at", -1)
            .limit(50)
        ]
        return cached if cached else normalized
