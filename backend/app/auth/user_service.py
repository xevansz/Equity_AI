from typing import Any

from motor.motor_asyncio import AsyncIOMotorDatabase

from app.auth.password_utils import hash_password, verify_password


class UserService:
    def __init__(self, db: AsyncIOMotorDatabase) -> None:
        self.collection = db.users

    @staticmethod
    def _normalize(email: str) -> str:
        return email.strip().lower()

    async def create_user(self, email: str, password: str, role: str = "user") -> None:
        """Create a new user in the database.

        Args:
            email: User email address
            password: Plain text password (will be hashed)
            role: User role (default: "user")
        """
        await self.collection.insert_one(
            {
                "email": self._normalize(email),
                "password": hash_password(password),
                "role": role,
            }
        )

    async def get_user(self, email: str) -> dict[str, Any] | None:
        """Retrieve a user by email.

        Args:
            email: User email address

        Returns:
            User document if found, None otherwise
        """
        return await self.collection.find_one({"email": self._normalize(email)})

    async def verify_user(self, email: str, password: str) -> dict[str, Any] | None:
        """Verify user credentials.

        Args:
            email: User email address
            password: Plain text password to verify

        Returns:
            User document if credentials are valid, None otherwise
        """
        user = await self.get_user(email)
        if not user:
            return None
        if not verify_password(password, user["password"]):
            return None
        return user

    async def update_password(self, email: str, new_password: str) -> bool:
        """Update user password.

        Args:
            email: User email address
            new_password: New plain text password (will be hashed)

        Returns:
            True if password was updated, False otherwise
        """
        hashed = hash_password(new_password)
        result = await self.collection.update_one({"email": self._normalize(email)}, {"$set": {"password": hashed}})
        return result.modified_count > 0
