"""Conversation Memory"""

from datetime import UTC, datetime

from motor.motor_asyncio import AsyncIOMotorDatabase


class ConversationMemory:
    def __init__(self, db: AsyncIOMotorDatabase | None) -> None:
        self.db = db

    async def save_message(self, session_id: str, role: str, content: str, user_id: str | None = None) -> None:
        if self.db is None:
            print(" Database not available, skipping message save")
            return

        doc: dict = {
            "session_id": session_id,
            "role": role,
            "content": content,
            "timestamp": datetime.now(UTC),
        }
        if user_id:
            doc["user_id"] = user_id

        await self.db.conversations.insert_one(doc)

    # TODO: pagination
    async def get_history(self, session_id: str, limit: int = 10) -> list[dict]:
        if self.db is None:
            return []

        cursor = self.db.conversations.find({"session_id": session_id}).sort("_id", -1).limit(limit)

        messages = await cursor.to_list(length=limit)
        return list(reversed(messages))

    async def get_sessions(self, user_id: str, limit: int = 20) -> list[dict]:
        """Return distinct sessions for a user ordered by most recent message."""
        if self.db is None:
            return []

        pipeline = [
            {"$match": {"user_id": user_id}},
            {"$sort": {"timestamp": -1}},
            {
                "$group": {
                    "_id": "$session_id",
                    "last_message": {"$first": "$content"},
                    "last_timestamp": {"$first": "$timestamp"},
                }
            },
            {"$sort": {"last_timestamp": -1}},
            {"$limit": limit},
        ]

        cursor = self.db.conversations.aggregate(pipeline)
        sessions = await cursor.to_list(length=limit)
        return [
            {
                "session_id": s["_id"],
                "last_message": s["last_message"],
                "last_timestamp": s["last_timestamp"],
            }
            for s in sessions
        ]
