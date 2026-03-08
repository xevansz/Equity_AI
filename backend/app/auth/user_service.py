from motor.motor_asyncio import AsyncIOMotorDatabase

from app.auth.password_utils import hash_password, verify_password


class UserService:
    def __init__(self, db: AsyncIOMotorDatabase) -> None:
        self.collection = db.users

    @staticmethod
    def _normalize(email: str) -> str:
        return email.strip().lower()

    async def create_user(self, email: str, password: str, role: str = "user") -> None:
        await self.collection.insert_one(
            {
                "email": self._normalize(email),
                "password": hash_password(password),
                "role": role,
            }
        )

    async def get_user(self, email: str) -> dict | None:
        return await self.collection.find_one({"email": self._normalize(email)})

    async def verify_user(self, email: str, password: str) -> dict | None:
        user = await self.get_user(email)
        if not user:
            return None
        if not verify_password(password, user["password"]):
            return None
        return user

    async def update_password(self, email: str, new_password: str) -> bool:
        hashed = hash_password(new_password)
        result = await self.collection.update_one(
            {"email": self._normalize(email)}, {"$set": {"password": hashed}}
        )
        return result.modified_count > 0
