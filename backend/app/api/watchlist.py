from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException, Path, Query

from app.dependencies import get_current_user, get_watchlist_service
from app.models.watchlist import WatchlistListResponse
from app.schemas.watchlist import WatchlistCreate
from app.services.watchlist_service import WatchlistService
from app.utils.validation import normalize_symbol, validate_symbol

router = APIRouter(prefix="/api", tags=["watchlist"])


@router.get("/watchlist", response_model=WatchlistListResponse)
async def get_watchlist(
    limit: int = Query(20, ge=1, le=100, description="Number of items to return"),
    after: datetime | None = Query(None, description="Cursor for pagination"),
    user: dict = Depends(get_current_user),
    service: WatchlistService = Depends(get_watchlist_service),
):
    return await service.get_watchlist(user["email"], limit=limit, after=after)


@router.post("/watchlist")
async def add_to_watchlist(
    item: WatchlistCreate,
    user: dict = Depends(get_current_user),
    service: WatchlistService = Depends(get_watchlist_service),
):
    added = await service.add_item(user["email"], item)
    if not added:
        raise HTTPException(status_code=400, detail="Company already in Watchlist")
    return {"message": "Added to Watchlist"}


@router.delete("/watchlist/{symbol}")
async def remove_from_watchlist(
    symbol: str = Path(..., min_length=1, max_length=20, description="Stock symbol"),
    user: dict = Depends(get_current_user),
    service: WatchlistService = Depends(get_watchlist_service),
):
    symbol = normalize_symbol(symbol)
    if not validate_symbol(symbol):
        raise HTTPException(status_code=400, detail="Invalid symbol format")

    removed = await service.remove_item(user["email"], symbol)
    if not removed:
        raise HTTPException(status_code=404, detail="Symbol not found")

    return {"message": "Removed from Watchlist"}
