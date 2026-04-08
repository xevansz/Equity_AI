"""Financial Data API"""

from fastapi import APIRouter, Depends, HTTPException, Query

from app.dependencies import get_current_user, get_data_service
from app.logging_config import get_logger
from app.schemas.financial import FinancialRequest, FinancialResponse
from app.services.data_service import DataService
from app.utils.validation import normalize_symbol, validate_symbol

logger = get_logger(__name__)

router = APIRouter(prefix="/api", tags=["financial"])


@router.post("/financial", response_model=FinancialResponse)
async def get_financial_data(
    request: FinancialRequest,
    user: dict = Depends(get_current_user),
    service: DataService = Depends(get_data_service),
) -> FinancialResponse:
    """Get financial data and metrics"""
    try:
        logger.info("Financial request: %s", request.symbol)
        data = await service.get_financial_data(request.symbol)
        logger.debug("Financial data loaded (keys=%s)", list(data.financials.keys()))

        return data
    except Exception as e:
        logger.exception("Financial API error")
        raise HTTPException(status_code=500, detail=str(e)) from e


@router.get("/financial/price")
async def get_stock_price(
    symbol: str = Query(..., min_length=1, max_length=20, description="Stock symbol"),
    user: dict = Depends(get_current_user),
    service: DataService = Depends(get_data_service),
):
    """Get current stock price"""
    try:
        symbol = normalize_symbol(symbol)
        if not validate_symbol(symbol):
            raise HTTPException(status_code=400, detail="Invalid symbol format")

        logger.info("Stock price request: %s", symbol)
        price_data = await service.get_stock_price(symbol)
        logger.debug("Stock price loaded: %s", price_data)
        return price_data
    except HTTPException:
        raise
    except Exception as e:
        logger.exception("Stock price API error")
        raise HTTPException(status_code=500, detail=str(e)) from e
