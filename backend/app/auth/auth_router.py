#backend/app/auth/auth_router.py
import os, secrets
from fastapi import APIRouter, Depends, HTTPException
from fastapi.security import OAuth2PasswordBearer
from app.dependencies import get_database, get_current_user
from app.auth.user_service import UserService
from app.auth.jwt_handler import create_token
from app.auth.smtp_service import send_email
from app.auth.schemas import RegisterRequest, LoginRequest, ResetPasswordRequest
from app.config import settings

router = APIRouter()
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="login")
ADMIN_EMAIL = os.getenv("ADMIN_EMAIL")
ADMIN_PASSWORD = os.getenv("ADMIN_PASSWORD")

otp_store = {}

# -------------------------
# REGISTER
# -------------------------
@router.post("/register")
async def register(data: RegisterRequest, db=Depends(get_database)):
    service = UserService(db)

    if await service.get_user(data.email):
        raise HTTPException(400, "User already exists")

    await service.create_user(data.email, data.password)
    return {"message": "Registered successfully"}


# -------------------------
# LOGIN
# -------------------------
@router.post("/login")
async def login(data: LoginRequest, db=Depends(get_database)):
    service = UserService(db)

    # Permanent Admin (from .env)
    if data.email == ADMIN_EMAIL and data.password == ADMIN_PASSWORD:
        token = create_token({"email": ADMIN_EMAIL, "role": "admin"})
        return {"access_token": token, "token_type": "bearer"}

    user = await service.verify_user(data.email, data.password)
    if not user:
        raise HTTPException(401, "Invalid credentials")

    token = create_token({"email": user["email"], "role": user["role"]})
    return {"access_token": token, "token_type": "bearer"}


# -------------------------
# CURRENT USER
# -------------------------
@router.get("/me")
def me(user=Depends(get_current_user)):
    return user


# -------------------------
# FORGOT PASSWORD (OTP)
# -------------------------
@router.post("/forgot-password")
async def forgot_password(email: str, db=Depends(get_database)):
    user = await db.users.find_one({"email": email})
    if not user:
        raise HTTPException(404, "User not found")

    otp = secrets.token_hex(3)
    otp_store[email] = otp

    send_email(
        to_email=email,
        subject="Your OTP",
        body=f"Your password reset OTP is: {otp}"
    )

    return {"message": "OTP sent to your email"}


# -------------------------
# RESET PASSWORD
# -------------------------
@router.post("/reset-password")
async def reset_password(data: ResetPasswordRequest, db=Depends(get_database)):
    if otp_store.get(data.email) != data.otp:
        raise HTTPException(400, "Invalid OTP")

    service = UserService(db)
    await service.update_password(data.email, data.new_password)

    del otp_store[data.email]
    return {"message": "Password updated successfully"}

"""
@router.post("/reset-password")
async def reset(data: dict, db=Depends(get_database)):
    email = data["email"]
    otp = data["otp"]
    new_password = data["new_password"]

    if otp_store.get(email) != otp:
        raise HTTPException(400, "Invalid OTP")

    service = UserService(db)
    updated = await service.update_password(email, new_password)

    if not updated:
        raise HTTPException(404, "User not found")

    del otp_store[email]
    return {"message": "Password updated successfully"}
"""