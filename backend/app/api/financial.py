"""Financial Data API"""

from fastapi import APIRouter, Depends, HTTPException

from app.dependencies import get_current_user, get_data_service
from app.schemas.financial import FinancialRequest, FinancialResponse
from app.services.data_service import DataService

router = APIRouter(tags=["financial"])


@router.post("/financial", response_model=FinancialResponse)
async def get_financial_data(
    request: FinancialRequest,
    user: dict = Depends(get_current_user),
    service: DataService = Depends(get_data_service),
) -> FinancialResponse:
    """Get financial data and metrics"""
    try:
        print("\nFINANCIAL REQUEST:", request.symbol)
        data = await service.get_financial_data(request.symbol)
        print("FINANCIAL DATA LOADED")
        print(data.financials.keys())
        print("-" * 60)

        return data
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e)) from e
