"""Configuration Management"""

# backend/app/config.py
from dotenv import load_dotenv
from pydantic_settings import BaseSettings

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
    TWELVE_DATA_API_KEYS: str = ""  # Comma-separated list of keys for rotation
    UPSTOX_API_KEYS: str = ""  # Comma-separated list of keys for rotation
    SEC_USER_AGENT: str = "EquityAI research-bot contact@example.com"

    # News APIs
    NEWSAPI_KEY: str = ""

    # Database
    MONGODB_URI: str = "mongodb://localhost:27017"
    DB_NAME: str = "equity_research"

    # JWT
    JWT_SECRET_KEY: str
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


def validate_jwt_secret() -> None:
    """Validate JWT secret key at startup.

    Raises:
        ValueError: If JWT_SECRET_KEY is missing or insecure
    """
    if not settings.JWT_SECRET_KEY:
        raise ValueError(
            "JWT_SECRET_KEY is not set. Please set JWT_SECRET_KEY in your .env file. "
            "Generate a secure secret with: openssl rand -hex 32"
        )

    if len(settings.JWT_SECRET_KEY) < 32:
        raise ValueError(
            f"JWT_SECRET_KEY is too short ({len(settings.JWT_SECRET_KEY)} characters). "
            "It must be at least 32 characters for security. "
            "Generate a secure secret with: openssl rand -hex 32"
        )

    if settings.JWT_SECRET_KEY in ["changeme", "secret", "test", "dev", "development"]:
        raise ValueError(
            "JWT_SECRET_KEY is using a common/insecure value. "
            "Please use a cryptographically secure random string. "
            "Generate one with: openssl rand -hex 32"
        )
