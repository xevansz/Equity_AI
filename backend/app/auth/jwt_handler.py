from datetime import UTC, datetime, timedelta
from typing import Any

from jose import JWTError, jwt

from app.config import settings
from app.exceptions import ConfigurationError

JWT_SECRET_KEY = settings.JWT_SECRET_KEY
ALGORITHM = "HS256"
JWT_EXPIRE_MINUTES = int(settings.JWT_EXPIRE_MINUTES)

if not JWT_SECRET_KEY:
    raise ConfigurationError("JWT_SECRET_KEY not found in environment")


def create_token(data: dict[str, Any]) -> str:
    """Create a JWT token with expiration.

    Args:
        data: Payload data to encode in the token

    Returns:
        Encoded JWT token string
    """
    payload = data.copy()
    payload["exp"] = datetime.now(UTC) + timedelta(minutes=JWT_EXPIRE_MINUTES)
    return jwt.encode(payload, JWT_SECRET_KEY, algorithm=ALGORITHM)


def verify_token(token: str) -> dict[str, Any] | None:
    """Verify and decode a JWT token.

    Args:
        token: JWT token string to verify

    Returns:
        Decoded payload if valid, None if invalid or expired
    """
    try:
        return jwt.decode(token, JWT_SECRET_KEY, algorithms=[ALGORITHM])
    except JWTError:
        return None
