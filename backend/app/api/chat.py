"""Chat API Endpoint"""

from fastapi import APIRouter, HTTPException, Depends
from schemas.chat import ChatRequest, ChatResponse
from services.chat_service import ChatService
from dependencies import get_database

router = APIRouter()


@router.post("/chat", response_model=ChatResponse)
async def chat(request: ChatRequest, db=Depends(get_database)):
    """Conversational chat with equity research"""
    try:
        print("\n📩 CHAT REQUEST:", request.query)

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
        raise HTTPException(status_code=500, detail=str(e))
