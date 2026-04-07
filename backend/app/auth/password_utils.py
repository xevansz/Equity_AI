import hashlib
import re

import bcrypt
from fastapi import HTTPException


def validate_password(password: str) -> None:
    """Validate password meets security requirements.

    Args:
        password: Password string to validate

    Raises:
        HTTPException: If password doesn't meet requirements
    """
    if len(password) < 8:
        raise HTTPException(400, "Password must be at least 8 characters")

    if not re.search(r"[A-Z]", password):
        raise HTTPException(400, "Password must contain at least one uppercase letter")

    if not re.search(r"[0-9]", password):
        raise HTTPException(400, "Password must contain at least one number")

    if not re.search(r"[!@#$%^&*]", password):
        raise HTTPException(400, "Password must contain at least one special character")


def _prehash(password: str) -> bytes:
    """Pre-hash password to avoid bcrypt 72-byte limit.

    Args:
        password: Password string to hash

    Returns:
        SHA256 hash of the password
    """
    return hashlib.sha256(password.encode("utf-8")).digest()


def hash_password(password: str) -> str:
    """Hash password using bcrypt with SHA256 pre-hashing.

    Args:
        password: Plain text password to hash

    Returns:
        Hashed password string

    Raises:
        HTTPException: If password doesn't meet validation requirements
    """
    validate_password(password)
    pre = _prehash(password)
    hashed = bcrypt.hashpw(pre, bcrypt.gensalt())
    return hashed.decode("utf-8")


def verify_password(plain: str, hashed: str) -> bool:
    """Verify a plain password against a hashed password.

    Args:
        plain: Plain text password to verify
        hashed: Hashed password to compare against

    Returns:
        True if password matches, False otherwise
    """
    pre = _prehash(plain)
    return bcrypt.checkpw(pre, hashed.encode("utf-8"))
