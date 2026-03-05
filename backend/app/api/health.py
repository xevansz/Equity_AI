from datetime import UTC, datetime

from fastapi import APIRouter, Depends
from motor.motor_asyncio import AsyncIOMotorDatabase

from app.dependencies import get_database
from app.schemas.health import HealthResponse

router = APIRouter(tags=["health"])


@router.get("/health", response_model=HealthResponse)
async def health(db: AsyncIOMotorDatabase = Depends(get_database)) -> HealthResponse:

    # db check
    try:
        await db.command("ping")
        db_status = "healthy"
    except Exception as e:
        db_status = f"unhealthy: {str(e)}"

    # LLM health check
    try:
        from app.llm.gemini import gemini

        if gemini:
            llm_status = "healthy"
        else:
            llm_status = "Unavailable"
    except Exception as e:
        llm_status = f"Unhealthy: str({e})"

    # TODO
    # add model loaded
    # and any other needed checks

    return HealthResponse(
        db_status=db_status,
        llm_status=llm_status,
        timestamp=datetime.now(UTC),
        service="api",
    )
