"""Financial Data API"""

from fastapi import APIRouter, HTTPException
from schemas.financial import FinancialRequest, FinancialResponse
from services.data_service import DataService

router = APIRouter()


@router.post("/financial", response_model=FinancialResponse)
async def get_financial_data(request: FinancialRequest):
    """Get financial data and metrics"""
    try:
        print("\n💰 FINANCIAL REQUEST:", request.symbol)
        service = DataService()
        data = await service.get_financial_data(request.symbol)
        print("📈 FINANCIAL DATA LOADED")
        print(data.financials.keys())
        print("-" * 60)

        service = DataService()
        data = await service.get_financial_data(request.symbol)

        return data
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
