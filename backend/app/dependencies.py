from fastapi import Depends, HTTPException, Request
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from motor.motor_asyncio import AsyncIOMotorDatabase

from app.auth.jwt_handler import verify_token
from app.auth.user_service import UserService
from app.conversational.memory import ConversationMemory
from app.database import database
from app.mcp.news_api import NewsAPI
from app.services.chat_service import ChatService
from app.services.data_service import DataService
from app.services.research_service import ResearchService

security = HTTPBearer()


# Database
def get_database():
    """returns the MongoDB database instance"""
    return database.get_database()


# JWT Auth
def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security)):
    """returns the current user from the JWT token"""
    token = credentials.credentials
    payload = verify_token(token)

    if not payload:
        raise HTTPException(status_code=401, detail="Invalid or expired token")

    return payload


def get_user_service(db: AsyncIOMotorDatabase = Depends(get_database)) -> UserService:
    return UserService(db)


def get_conversation_memory(db: AsyncIOMotorDatabase = Depends(get_database)) -> ConversationMemory:
    return ConversationMemory(db)


def get_chat_service(
    db: AsyncIOMotorDatabase = Depends(get_database),
    user: dict = Depends(get_current_user),
) -> ChatService:
    user_id = user.get("email") if isinstance(user, dict) else None
    return ChatService(db, user_id=user_id)


def get_data_service() -> DataService:
    return DataService()


def get_research_service(db: AsyncIOMotorDatabase = Depends(get_database)) -> ResearchService:
    return ResearchService(db)


def get_news_api(request: Request) -> NewsAPI:
    client = getattr(request.app.state, "news_api", None)
    if client is not None:
        return client
    return NewsAPI()


# Admin only
def admin_only(user=Depends(get_current_user)):
    """returns the current user if they are an admin"""
    if user.get("role") != "admin":
        raise HTTPException(status_code=403, detail="Admins only")
    return user
