"""Chat API Endpoint"""

from backend.app import database
from backend.app.models.user import User
from fastapi import APIRouter, Depends, HTTPException

from app.dependencies import get_current_user, get_database
from app.schemas.chat import ChatRequest, ChatResponse
from app.services.chat_service import ChatService

router = APIRouter()


@router.post("/chat", response_model=ChatResponse)
async def chat(
    request: ChatRequest,
    db: database = Depends(get_database),
    user: User = Depends(get_current_user),
):
    """Conversational chat with equity research"""
    try:
        print("\nCHAT REQUEST:", request.query)

        if db is None:
            raise HTTPException(status_code=503, detail="Database not available")

        service = ChatService(db)
        response = await service.process_query(request)

        print("🤖 CHAT RESPONSE:", response.answer)
        print("-" * 60)

        return response
    except HTTPException:
        raise
    except Exception as e:
        print(f"CHAT API ERROR: {repr(e)}")
        raise HTTPException(status_code=500, detail=str(e)) from e
