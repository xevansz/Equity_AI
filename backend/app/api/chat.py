"""Chat API Endpoint"""

from fastapi import APIRouter, Depends, HTTPException
from motor.motor_asyncio import AsyncIOMotorDatabase

from app.dependencies import get_chat_service, get_current_user, get_database
from app.schemas.chat import ChatRequest, ChatResponse
from app.services.chat_service import ChatService

router = APIRouter(tags=["chat"])


@router.post("/chat", response_model=ChatResponse)
async def chat(
    request: ChatRequest,
    db: AsyncIOMotorDatabase = Depends(get_database),
    user: dict = Depends(get_current_user),
    service: ChatService = Depends(get_chat_service),
) -> ChatResponse:
    """Conversational chat with equity research"""
    try:
        print("\nCHAT REQUEST:", request.query)

        if db is None:
            raise HTTPException(status_code=503, detail="Database not available")
        response = await service.process_query(request)

        print("🤖 CHAT RESPONSE:", response.answer)
        print("-" * 60)

        return response
    except HTTPException:
        raise
    except Exception as e:
        print(f"CHAT API ERROR: {repr(e)}")
        raise HTTPException(status_code=500, detail=str(e)) from e
