"""OTP DB Document Model"""

from datetime import UTC, datetime

from pydantic import BaseModel, EmailStr, Field


class OtpDocument(BaseModel):
    email: EmailStr
    otp: str
    created_at: datetime = Field(default_factory=lambda: datetime.now(UTC))
