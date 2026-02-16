from motor.motor_asyncio import AsyncIOMotorDatabase
from datetime import datetime, UTC
from typing import Optional


class SymbolCacheService:
  def __init__(self, db: AsyncIOMotorDatabase):
    self.collection = db.get_collection("symbol_cache")

  async def get_symbol(self, query: str) -> Optional[str]:
    """Search for symbol in cache"""
    normalized = query.lower().strip()

    result = await self.collection.find_one(
      {"$or": [{"company_name": normalized}, {"aliases": normalized}]}
    )

    if result:
      await self.collection.update_one(
        {"_id": result["_id"]},
        {"$set": {"last_used": datetime.now(UTC)}, "$inc": {"use_count": 1}},
      )
      return result["symbol"]

    return None

  async def cache_symbol(self, company_name: str, symbol: str):
    """store new symbol"""
    normalized = company_name.lower().strip()

    # Check if already exists
    existing = await self.collection.find_one({"symbol": symbol})
    if existing:
      # Add as alias if it's a new variation
      if normalized not in existing.get("aliases", []):
        await self.collection.update_one(
          {"_id": existing["_id"]}, {"$addToSet": {"aliases": normalized}}
        )
      return

    # Insert new entry
    await self.collection.insert_one(
      {
        "company_name": normalized,
        "symbol": symbol,
        "display_name": company_name,
        "aliases": [normalized],
        "created_at": datetime.now(UTC),
        "last_used": datetime.now(UTC),
        "use_count": 1,
      }
    )
