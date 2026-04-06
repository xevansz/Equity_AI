"""Chat API Endpoint"""

from fastapi import APIRouter, Depends, HTTPException
from motor.motor_asyncio import AsyncIOMotorDatabase

from app.dependencies import get_chat_service, get_current_user, get_database
from app.logging_config import get_logger
from app.schemas.chat import ChatRequest, ChatResponse
from app.services.chat_service import ChatService

logger = get_logger(__name__)

router = APIRouter(prefix="/api", tags=["chat"])


@router.post("/chat", response_model=ChatResponse)
async def chat(
    request: ChatRequest,
    db: AsyncIOMotorDatabase = Depends(get_database), # type: ignore
    user: dict = Depends(get_current_user),
    service: ChatService = Depends(get_chat_service),
) -> ChatResponse:
    """Conversational chat with equity research"""
    try:
        logger.info("CHAT REQUEST: %s", request.query)
        if db is None:
            raise HTTPException(status_code=503, detail="Database not available")
        response = await service.process_query(request)
        logger.info("CHAT RESPONSE: %s", response.answer)
        return response
    except HTTPException:
        raise
    except Exception as e:
        logger.exception("CHAT API ERROR: %s", repr(e))
        raise HTTPException(status_code=500, detail=str(e)) from e
