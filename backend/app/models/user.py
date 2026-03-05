from pydantic import BaseModel, EmailStr


class User(BaseModel):
    id: str | None = None
    email: EmailStr
    hashed_password: str
    role: str = "user"  # user | admin
