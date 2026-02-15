"""Conversation Memory"""

from datetime import datetime


class ConversationMemory:
    def __init__(self, db):
        self.db = db

    async def save_message(self, session_id: str, role: str, content: str):
        if self.db is None:
            print(" Database not available, skipping message save")
            return

        await self.db.conversations.insert_one(
            {
                "session_id": session_id,
                "role": role,
                "content": content,
                "timestamp": datetime.utcnow(),
            }
        )

    # TODO: pagination
    async def get_history(self, session_id: str, limit: int = 10):
        if self.db is None:
            return []

        cursor = (
            self.db.conversations.find({"session_id": session_id})
            .sort("_id", -1)
            .limit(limit)
        )

        messages = await cursor.to_list(length=limit)
        return list(reversed(messages))
