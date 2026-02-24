from fastapi import APIRouter, Depends
from app.dependencies import get_database
from datetime import UTC, datetime

router = APIRouter()


@router.get("/health")
async def health(db=Depends(get_database)):

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

    return {
        "DB Status": db_status,
        "LLM Status": llm_status,
        "timestamp": datetime.now(UTC),
        "service": "api",
    }
