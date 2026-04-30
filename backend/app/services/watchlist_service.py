"""Watchlist Service"""

from datetime import UTC, datetime

from motor.motor_asyncio import AsyncIOMotorDatabase

from app.models.watchlist import WatchlistItemOut, WatchlistListResponse
from app.schemas.watchlist import WatchlistCreate


class WatchlistService:
    def __init__(self, db: AsyncIOMotorDatabase) -> None:
        self.collection = db.watchlist

    async def get_watchlist(
        self,
        user_id: str,
        limit: int = 20,
        after: datetime | None = None,
    ) -> WatchlistListResponse:
        """Fetch paginated watchlist for a user.

        Args:
            user_id: User identifier (email)
            limit: Maximum number of items to return
            after: Cursor datetime for pagination

        Returns:
            WatchlistListResponse with items and next cursor
        """
        query: dict = {"user_id": user_id}
        if after:
            query["added_at"] = {"$lt": after}

        cursor = self.collection.find(query).sort("added_at", -1).limit(limit)
        raw_items = await cursor.to_list(length=limit)

        items = [
            WatchlistItemOut(
                symbol=doc["symbol"],
                name=doc["name"],
                company_name=doc.get("company_name", doc["name"]),
                added_at=doc["added_at"],
            )
            for doc in raw_items
        ]

        next_cursor = raw_items[-1]["added_at"] if raw_items else None
        return WatchlistListResponse(items=items, next_cursor=next_cursor, limit=limit)

    async def add_item(self, user_id: str, item: WatchlistCreate) -> bool:
        """Add a company to the user's watchlist.

        Args:
            user_id: User identifier (email)
            item: Watchlist item to add

        Returns:
            True if added, False if already exists
        """
        normalized_name = item.company_name.lower().strip()

        existing = await self.collection.find_one(
            {"user_id": user_id, "normalized_name": normalized_name}
        )
        if existing:
            return False

        new_item = {
            "symbol": item.symbol,
            "name": item.name,
            "company_name": item.company_name,
            "normalized_name": normalized_name,
            "user_id": user_id,
            "added_at": datetime.now(UTC),
        }
        await self.collection.insert_one(new_item)
        return True

    async def remove_item(self, user_id: str, symbol: str) -> bool:
        """Remove a symbol from the user's watchlist.

        Args:
            user_id: User identifier (email)
            symbol: Stock symbol to remove

        Returns:
            True if deleted, False if not found
        """
        result = await self.collection.delete_one({"user_id": user_id, "symbol": symbol})
        return result.deleted_count > 0
