from datetime import UTC, datetime

from fastapi import APIRouter, Depends, HTTPException, Query

from app import database
from app.dependencies import get_current_user, get_database
from app.models.user import User
from app.models.watchlist import WatchlistCreate

router = APIRouter(tags=["watchlist"])


@router.get("/watchlist")
async def get_watchlist(
    limit: int = 20,
    after: datetime | None = Query(None),
    db: database = Depends(get_database),
    user: User = Depends(get_current_user),
):
    query = {"user_id": user.id}

    if after:
        query["added_at"] = {"$lt": after}

    cursor = db.watchlist.find(query).sort("added_at", -1).limit(limit)

    items = await cursor.to_list(length=limit)

    # Determine next cursor
    next_cursor = None
    if items:
        next_cursor = items[-1]["added_at"]

    return {
        "items": items,
        "next_cursor": next_cursor,
        "limit": limit,
    }


@router.post("/watchlist")
async def add_to_watchlist(
    item: WatchlistCreate,
    db: database = Depends(get_database),
    user: User = Depends(get_current_user),
):
    # don't save duplicates
    existing = await db.watchlist.find_one({"user_id": user.id, "symbol": item.symbol})

    if existing:
        raise HTTPException(status_code=400, detail="Symbol already in Watchlist")

    new_item = {
        "symbol": item.symbol,
        "name": item.name,
        "user_id": user.id,
        "added_at": datetime.now(UTC),
    }

    await db.watchlist.insert_one(new_item)

    return {"message": "Added to Watchlist"}


@router.delete("/watchlist/{symbol}")
async def remove_from_watchlist(
    symbol: str,
    db: database = Depends(get_database),
    user: User = Depends(get_current_user),
):
    result = await db.watchlist.delete_one({"user_id": user.id, "symbol": symbol})

    if result.deleted_count == 0:
        raise HTTPException(status_code=404, detail="Symbol not found")

    return {"message": "Removed from Watchlist"}
