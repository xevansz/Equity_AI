from datetime import UTC, datetime

from motor.motor_asyncio import AsyncIOMotorDatabase
from pymongo.errors import DuplicateKeyError

from app.utils.normalization import normalize_company_name


class SymbolCacheService:
    def __init__(self, db: AsyncIOMotorDatabase):
        self.symbols = db.get_collection("symbols")
        self.aliases = db.get_collection("symbol_aliases")

    async def get_symbol(self, query: str) -> str | None:
        """Search for symbol via normalized alias lookup."""
        normalized = normalize_company_name(query)

        result = await self.aliases.find_one_and_update(
            {"normalized_alias": normalized},
            {"$set": {"last_used": datetime.now(UTC)}, "$inc": {"use_count": 1}},
            return_document=True,
        )

        if result:
            return result["symbol"]

        return None

    async def cache_alias(self, company_name: str, symbol: str, canonical_name: str | None = None):
        """Store a company name alias pointing to symbol.

        - Ensures symbol exists in symbols collection.
        - Inserts alias if normalized form doesn't already exist globally.
        """
        now = datetime.now(UTC)
        symbol = symbol.strip().upper()
        normalized = normalize_company_name(company_name)

        if not normalized:
            return

        await self.symbols.update_one(
            {"_id": symbol},
            {"$setOnInsert": {"canonical_name": canonical_name or company_name.strip(), "created_at": now}},
            upsert=True,
        )

        try:
            await self.aliases.update_one(
                {"normalized_alias": normalized},
                {
                    "$setOnInsert": {
                        "symbol": symbol,
                        "alias_name": company_name.strip(),
                        "normalized_alias": normalized,
                        "created_at": now,
                        "last_used": now,
                        "use_count": 0,
                    }
                },
                upsert=True,
            )
        except DuplicateKeyError:
            pass
