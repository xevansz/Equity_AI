"""Conversations API"""

from fastapi import APIRouter, Depends
from motor.motor_asyncio import AsyncIOMotorDatabase

from app.conversational.memory import ConversationMemory
from app.dependencies import get_conversation_memory, get_current_user, get_database

router = APIRouter(prefix="/api", tags=["conversations"])


@router.get("/conversations")
async def get_conversations(
    db: AsyncIOMotorDatabase = Depends(get_database),
    user: dict = Depends(get_current_user),
    memory: ConversationMemory = Depends(get_conversation_memory),
) -> list[dict]:
    sessions = await memory.get_sessions(user_id=user["email"])
    return sessions


@router.get("/conversations/{session_id}")
async def get_conversation(
    session_id: str,
    db: AsyncIOMotorDatabase = Depends(get_database),
    user: dict = Depends(get_current_user),
    memory: ConversationMemory = Depends(get_conversation_memory),
) -> list[dict]:
    messages = await memory.get_history(session_id=session_id)
    return messages
