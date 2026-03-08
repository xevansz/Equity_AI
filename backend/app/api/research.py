"""Research Report API"""

from fastapi import APIRouter, Depends
from motor.motor_asyncio import AsyncIOMotorDatabase

from app.dependencies import get_current_user, get_database
from app.llm.report_generator import generate_equity_report
from app.logging_config import get_logger
from app.schemas.research import ResearchRequest, ResearchResponse

logger = get_logger(__name__)

router = APIRouter(prefix="/api", tags=["research"])


@router.post("/research", response_model=ResearchResponse)
async def research(
    req: ResearchRequest,
    db: AsyncIOMotorDatabase = Depends(get_database),
    user: dict = Depends(get_current_user),
) -> ResearchResponse:
    logger.info("Research request: %s", req.symbol)
    report = generate_equity_report(req.symbol, db)
    logger.info("Research report generated")
    logger.debug("Data-CoT preview: %s", report.get("Data_CoT", "")[:150])
    logger.debug("Thesis-CoT preview: %s", report.get("Thesis_CoT", "")[:150])
    logger.debug("Risk-CoT preview: %s", report.get("Risk_CoT", "")[:150])

    return ResearchResponse(**report)
