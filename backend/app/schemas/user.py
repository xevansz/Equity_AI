from pydantic import BaseModel, EmailStr


class UserOut(BaseModel):
    id: str | None
    email: EmailStr
    role: str


# Used when registering
class RegisterRequest(BaseModel):
    email: EmailStr
    password: str


# Used when logging in
class LoginRequest(BaseModel):
    email: EmailStr
    password: str


# Used inside JWT token
class TokenData(BaseModel):
    email: EmailStr
    role: str


class ResetPasswordRequest(BaseModel):
    email: EmailStr
    otp: str
    new_password: str


class ForgotPasswordRequest(BaseModel):
    email: EmailStr


class TokenResponse(BaseModel):
    access_token: str
    token_type: str


class MessageResponse(BaseModel):
    message: str
