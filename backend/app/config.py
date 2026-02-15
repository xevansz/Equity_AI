"""Configuration Management"""

# backend/app/config.py
from pydantic_settings import BaseSettings
from dotenv import load_dotenv

load_dotenv()


class Settings(BaseSettings):
    # Server
    HOST: str = "0.0.0.0"
    PORT: int = 8000

    # LLM
    GEMINI_API_KEY: str = ""
    GEMINI_MODEL: str = "gemini-2.5-flash"

    # Financial APIs
    ALPHA_VANTAGE_API_KEY: str = ""
    FINNHUB_API_KEY: str = ""

    # News APIs
    NEWSAPI_KEY: str = ""

    # Database
    MONGODB_URI: str = "mongodb://localhost:27017"
    DB_NAME: str = "equity_research"

    # JWT
    JWT_SECRET_KEY: str = "youlikemychinesedecorations?"
    JWT_EXPIRE_MINUTES: int = 1440

    # Admin
    ADMIN_EMAIL: str
    ADMIN_PASSWORD: str

    # SMTP
    SMTP_HOST: str = ""
    SMTP_PORT: int = 587
    SMTP_EMAIL: str = ""
    SMTP_PASSWORD: str = ""

    # Google OAuth
    GOOGLE_CLIENT_ID: str = ""
    GOOGLE_CLIENT_SECRET: str = ""

    # Vector Store
    CHROMA_PERSIST_DIR: str = "vector_db"
    EMBEDDING_MODEL: str = "all-MiniLM-L6-v2"
    TOP_K_RETRIEVAL: int = 5

    class Config:
        env_file = ".env"
        extra = "allow"


settings = Settings()
