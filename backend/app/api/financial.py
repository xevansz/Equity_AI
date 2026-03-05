"""Financial Data API"""

from fastapi import APIRouter, Depends, HTTPException

from app.dependencies import get_current_user, get_data_service
from app.logging_config import get_logger
from app.schemas.financial import FinancialRequest, FinancialResponse
from app.services.data_service import DataService

logger = get_logger(__name__)

router = APIRouter(tags=["financial"])


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
