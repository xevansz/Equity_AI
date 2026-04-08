"""Chat API Endpoint"""

from typing import Any

from fastapi import APIRouter, Depends, HTTPException
from motor.motor_asyncio import AsyncIOMotorDatabase

from app.dependencies import get_chat_service, get_current_user, get_database
from app.exceptions import DatabaseError
from app.logging_config import get_logger
from app.schemas.chat import ChatRequest, ChatResponse
from app.services.chat_service import ChatService

logger = get_logger(__name__)

router = APIRouter(prefix="/api", tags=["chat"])


@router.post("/chat", response_model=ChatResponse)
async def chat(
    request: ChatRequest,
    db: AsyncIOMotorDatabase | None = Depends(get_database),
    user: dict[str, Any] = Depends(get_current_user),
    service: ChatService = Depends(get_chat_service),
) -> ChatResponse:
    """Conversational chat with equity research.

    Args:
        request: Chat request with query and session_id
        db: Database connection
        user: Current authenticated user
        service: Chat service instance

    Returns:
        ChatResponse with answer and sources

    Raises:
        HTTPException: If database unavailable or processing fails
    """
    try:
        logger.info("CHAT REQUEST: %s", request.query)
        if db is None:
            raise DatabaseError("Database not available")
        response = await service.process_query(request)
        logger.info("CHAT RESPONSE: %s", response.answer)
        return response
    except DatabaseError as e:
        logger.error("Database error in chat: %s", e.message)
        raise HTTPException(status_code=503, detail=e.message) from e
    except HTTPException:
        raise
    except Exception as e:
        logger.exception("CHAT API ERROR: %s", repr(e))
        raise HTTPException(status_code=500, detail=str(e)) from e
