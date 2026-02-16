"""Database Initialization"""

from motor.motor_asyncio import AsyncIOMotorClient
from app.config import settings


class Database:
    def __init__(self):
        self.client = None
        self.db = None

    async def connect(self):
        self.client = AsyncIOMotorClient(settings.MONGODB_URI)
        self.db = self.client[settings.DB_NAME]
        print("MongoDB connected")

    async def close(self):
        if self.client:
            self.client.close()
            print("Mongodb disconnected")

    def get_database(self):
        return self.db


database = Database()


async def init_databases():
    await database.connect()


async def close_databases():
    await database.close()
