"""Research Report API"""

from fastapi import APIRouter, Depends
from motor.motor_asyncio import AsyncIOMotorDatabase

from app.dependencies import get_current_user, get_database
from app.llm.report_generator import generate_equity_report
from app.schemas.research import ResearchRequest, ResearchResponse

router = APIRouter(tags=["research"])


@router.post("/research", response_model=ResearchResponse)
async def research(
    req: ResearchRequest,
    db: AsyncIOMotorDatabase = Depends(get_database),
    user: dict = Depends(get_current_user),
) -> ResearchResponse:
    print("\nRESEARCH REQUEST:", req.symbol)
    report = generate_equity_report(req.symbol, db)
    print("RESEARCH REPORT GENERATED")

    print("Data-CoT:", report["Data_CoT"][:150])
    print("Thesis-CoT:", report["Thesis_CoT"][:150])
    print("Risk-CoT:", report["Risk_CoT"][:150])
    print("-" * 60)

    return ResearchResponse(**report)
