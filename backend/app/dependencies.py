from fastapi import Depends, HTTPException
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from app.auth.jwt_handler import verify_token
from app.database import database

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


# Admin only
def admin_only(user=Depends(get_current_user)):
    """returns the current user if they are an admin"""
    if user.get("role") != "admin":
        raise HTTPException(status_code=403, detail="Admins only")
    return user
