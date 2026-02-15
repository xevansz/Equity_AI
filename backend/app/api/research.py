"""Research Report API"""

from fastapi import APIRouter
from pydantic import BaseModel
from research_engine.report_generator import generate_equity_report
from fastapi import Depends
from dependencies import get_database

router = APIRouter()


class ResearchRequest(BaseModel):
    symbol: str


@router.post("/research")
async def research(req: ResearchRequest, db=Depends(get_database)):
    print("\n📊 RESEARCH REQUEST:", req.symbol)
    report = generate_equity_report(req.symbol, db)
    print("📝 RESEARCH REPORT GENERATED")

    print("🧠 Data-CoT:", report["Data_CoT"][:150])
    print("📈 Thesis-CoT:", report["Thesis_CoT"][:150])
    print("⚠️ Risk-CoT:", report["Risk_CoT"][:150])
    print("-" * 60)

    return report
