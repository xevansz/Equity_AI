from datetime import UTC, datetime

from fastapi import APIRouter, Depends, HTTPException, Path, Query
from motor.motor_asyncio import AsyncIOMotorDatabase

from app.dependencies import get_current_user, get_database
from app.models.watchlist import WatchlistItemOut, WatchlistListResponse
from app.schemas.watchlist import WatchlistCreate
from app.utils.validation import normalize_symbol, validate_symbol

router = APIRouter(prefix="/api", tags=["watchlist"])


@router.get("/watchlist", response_model=WatchlistListResponse)
async def get_watchlist(
    limit: int = Query(20, ge=1, le=100, description="Number of items to return"),
    after: datetime | None = Query(None, description="Cursor for pagination"),
    db: AsyncIOMotorDatabase = Depends(get_database),
    user: dict = Depends(get_current_user),
):
    if db is None:
        raise HTTPException(status_code=503, detail="Database not available")

    query: dict = {"user_id": user["email"]}

    if after:
        query["added_at"] = {"$lt": after}

    cursor = db.watchlist.find(query).sort("added_at", -1).limit(limit)

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


@router.post("/watchlist")
async def add_to_watchlist(
    item: WatchlistCreate,
    db: AsyncIOMotorDatabase = Depends(get_database),
    user: dict = Depends(get_current_user),
):
    if db is None:
        raise HTTPException(status_code=503, detail="Database not available")

    # Normalize company name for duplicate detection
    normalized_name = item.company_name.lower().strip()

    # don't save duplicates
    existing = await db.watchlist.find_one(
        {
            "user_id": user["email"],
            "normalized_name": normalized_name,
        }
    )

    if existing:
        raise HTTPException(status_code=400, detail="Company already in Watchlist")

    new_item = {
        "symbol": item.symbol,
        "name": item.name,
        "company_name": item.company_name,
        "normalized_name": normalized_name,
        "user_id": user["email"],
        "added_at": datetime.now(UTC),
    }

    await db.watchlist.insert_one(new_item)

    return {"message": "Added to Watchlist"}


@router.delete("/watchlist/{symbol}")
async def remove_from_watchlist(
    symbol: str = Path(..., min_length=1, max_length=20, description="Stock symbol"),
    db: AsyncIOMotorDatabase = Depends(get_database),
    user: dict = Depends(get_current_user),
):
    if db is None:
        raise HTTPException(status_code=503, detail="Database not available")

    symbol = normalize_symbol(symbol)
    if not validate_symbol(symbol):
        raise HTTPException(status_code=400, detail="Invalid symbol format")

    result = await db.watchlist.delete_one({"user_id": user["email"], "symbol": symbol})

    if result.deleted_count == 0:
        raise HTTPException(status_code=404, detail="Symbol not found")

    return {"message": "Removed from Watchlist"}
