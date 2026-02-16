"""Health Check"""

from fastapi import APIRouter, Depends
from app.dependencies import get_database, admin_only
from datetime import UTC, datetime

router = APIRouter()


@router.get("/health")
async def health(admin=Depends(admin_only)):
    db = get_database()
    if not db:
        return {"status": "unhealthy"}

    # TODO: add LLM checks

    return {
        "status": "healthy",
        "timestamp": datetime.now(datetime.timezone(UTC)),
        "service": "api",
    }
