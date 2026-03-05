"""Database Initialization"""

from motor.motor_asyncio import AsyncIOMotorClient
from pymongo.errors import PyMongoError

from app.config import settings
from app.logging_config import get_logger

logger = get_logger(__name__)


class Database:
    def __init__(self):
        self.client = None
        self.db = None

    async def connect(self):
        try:
            self.client = AsyncIOMotorClient(settings.MONGODB_URI, serverSelectionTimeoutMS=5000)
            self.db = self.client[settings.DB_NAME]

            await self.client.admin.command("ping")

            logger.info("MongoDB connected successfully")

        except PyMongoError:
            logger.exception("MongoDB connection failed")
            raise

    async def close(self):
        if self.client:
            self.client.close()
            logger.info("MongoDB disconnected")

    def get_database(self):
        return self.db

    async def create_index_symbol(self):  # Do we need this?
        if self.db is not None:
            collection = self.db["symbol_cache"]
            await collection.create_index([("symbol", 1)])

    async def create_index_watchlist(self):
        if self.db is not None:
            await self.db.watchlist.create_index([("user_id", 1), ("symbol", 1)], unique=True)
            # obj = await self.db.watchlist.find({"user_id": user_id}).explain("executionStats")
            # if obg is COLLSCAN we need an index

    async def create_index_users(self):
        if self.db is not None:
            await self.db.users.create_index("email", unique=True)

    async def create_index_conversations(self):
        if self.db is not None:
            await self.db.conversations.create_index([("user_id", 1), ("created_at", -1)])
            await self.db.conversations.create_index("session_id")

    async def create_index_otps(self):
        if self.db is not None:
            await self.db.otps.create_index("created_at", expireAfterSeconds=600)
            await self.db.otps.create_index("email")


database = Database()


async def init_databases():
    await database.connect()


async def close_databases():
    await database.close()


async def create_index_cache():
    await database.create_index_symbol()
    await database.create_index_watchlist()
    await database.create_index_users()
    await database.create_index_conversations()
    await database.create_index_otps()
