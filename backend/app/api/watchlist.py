from datetime import UTC, datetime

from fastapi import APIRouter, Depends, HTTPException, Query
from motor.motor_asyncio import AsyncIOMotorDatabase

from app.dependencies import get_current_user, get_database
from app.models.watchlist import WatchlistItemOut, WatchlistListResponse
from app.schemas.watchlist import WatchlistCreate

router = APIRouter(prefix="/api", tags=["watchlist"])


@router.get("/watchlist", response_model=WatchlistListResponse)
async def get_watchlist(
    limit: int = 20,
    after: datetime | None = Query(None),
    db: AsyncIOMotorDatabase = Depends(get_database),
    user: dict = Depends(get_current_user),
):
    query: dict = {"user_id": user["email"]}

    if after:
        query["added_at"] = {"$lt": after}

    cursor = db.watchlist.find(query).sort("added_at", -1).limit(limit)

    raw_items = await cursor.to_list(length=limit)

    items = [
        WatchlistItemOut(
            symbol=doc["symbol"],
            name=doc["name"],
            added_at=doc["added_at"],
        )
        for doc in raw_items
    ]

    next_cursor = raw_items[-1]["added_at"] if raw_items else None

    return WatchlistListResponse(items=items, next_cursor=next_cursor, limit=limit)


@router.post("/watchlist")
async def add_to_watchlist(
    item: WatchlistCreate,
    db: AsyncIOMotorDatabase = Depends(get_database),
    user: dict = Depends(get_current_user),
):
    # don't save duplicates
    existing = await db.watchlist.find_one({"user_id": user["email"], "symbol": item.symbol})

    if existing:
        raise HTTPException(status_code=400, detail="Symbol already in Watchlist")

    new_item = {
        "symbol": item.symbol,
        "name": item.name,
        "user_id": user["email"],
        "added_at": datetime.now(UTC),
    }

    await db.watchlist.insert_one(new_item)

    return {"message": "Added to Watchlist"}


@router.delete("/watchlist/{symbol}")
async def remove_from_watchlist(
    symbol: str,
    db: AsyncIOMotorDatabase = Depends(get_database),
    user: dict = Depends(get_current_user),
):
    result = await db.watchlist.delete_one({"user_id": user["email"], "symbol": symbol})

    if result.deleted_count == 0:
        raise HTTPException(status_code=404, detail="Symbol not found")

    return {"message": "Removed from Watchlist"}
