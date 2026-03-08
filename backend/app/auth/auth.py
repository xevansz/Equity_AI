import os
import secrets

from fastapi import APIRouter, Depends, HTTPException
from fastapi.security import OAuth2PasswordBearer
from motor.motor_asyncio import AsyncIOMotorDatabase

from app.auth.jwt_handler import create_token
from app.auth.smtp_service import send_email
from app.auth.user_service import UserService
from app.dependencies import get_current_user, get_database, get_user_service
from app.models.otp import OtpDocument
from app.schemas.user import (
    ForgotPasswordRequest,
    LoginRequest,
    MessageResponse,
    RegisterRequest,
    ResetPasswordRequest,
    TokenResponse,
)

router = APIRouter(prefix="/api/auth", tags=["auth"])
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/auth/login")
ADMIN_EMAIL = os.getenv("ADMIN_EMAIL")
ADMIN_PASSWORD = os.getenv("ADMIN_PASSWORD")


# REGISTER
@router.post("/register", response_model=MessageResponse)
async def register(
    data: RegisterRequest,
    service: UserService = Depends(get_user_service),
) -> MessageResponse:

    if await service.get_user(data.email):
        raise HTTPException(400, "User already exists")

    await service.create_user(data.email, data.password)
    return MessageResponse(message="Registered successfully")


# LOGIN
@router.post("/login", response_model=TokenResponse)
async def login(
    data: LoginRequest,
    service: UserService = Depends(get_user_service),
) -> TokenResponse:

    # Permanent Admin (from .env)
    if data.email == ADMIN_EMAIL and data.password == ADMIN_PASSWORD:
        token = create_token({"email": ADMIN_EMAIL, "role": "admin"})
        return TokenResponse(access_token=token, token_type="bearer")

    user = await service.verify_user(data.email, data.password)
    if not user:
        raise HTTPException(401, "Invalid credentials")

    token = create_token({"email": user["email"], "role": user["role"]})
    return TokenResponse(access_token=token, token_type="bearer")


# CURRENT USER
@router.get("/me")
def me(user=Depends(get_current_user)):
    return user


# FORGOT PASSWORD (OTP)
@router.post("/forgot-password", response_model=MessageResponse)
async def forgot_password(
    data: ForgotPasswordRequest, db: AsyncIOMotorDatabase = Depends(get_database)
) -> MessageResponse:
    email = data.email
    user = await db.users.find_one({"email": email})
    if not user:
        raise HTTPException(404, "User not found")

    otp = secrets.token_hex(3)

    await db.otps.delete_many({"email": email})
    otp_doc = OtpDocument(email=email, otp=otp)
    await db.otps.insert_one(otp_doc.model_dump())

    send_email(to_email=email, subject="Your OTP", body=f"Your password reset OTP is: {otp}")

    return MessageResponse(message="OTP sent to your email")


# RESET PASSWORD
@router.post("/reset-password", response_model=MessageResponse)
async def reset_password(
    data: ResetPasswordRequest,
    db: AsyncIOMotorDatabase = Depends(get_database),
    service: UserService = Depends(get_user_service),
) -> MessageResponse:
    doc = await db.otps.find_one({"email": data.email, "otp": data.otp})
    if not doc:
        raise HTTPException(400, "Invalid or expired OTP")

    await service.update_password(data.email, data.new_password)

    await db.otps.delete_one({"_id": doc["_id"]})
    return MessageResponse(message="Password updated successfully")
