"""Financial Data API"""

from fastapi import APIRouter, HTTPException, Depends
from app.schemas.financial import FinancialRequest, FinancialResponse
from app.services.data_service import DataService
from app.dependencies import get_current_user

router = APIRouter()


@router.post("/financial", response_model=FinancialResponse)
async def get_financial_data(
    request: FinancialRequest,
    user=Depends(get_current_user),
):
    """Get financial data and metrics"""
    try:
        print("\nFINANCIAL REQUEST:", request.symbol)
        service = DataService()
        data = await service.get_financial_data(request.symbol)
        print("FINANCIAL DATA LOADED")
        print(data.financials.keys())
        print("-" * 60)

        return data
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
