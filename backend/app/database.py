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

    async def create_index(self):
        if self.db is not None:
            await self.db.watchlist.create_index("user_id")

            # symbol resolver
            await self.db.symbol_aliases.create_index("normalized_alias", unique=True)
            await self.db.symbol_aliases.create_index([("symbol", 1), ("normalized_alias", 1)], unique=True)

            # Watchlist
            await self.db.watchlist.create_index([("user_id", 1), ("symbol", 1)], unique=True)
            # obj = await self.db.watchlist.find({"user_id": user_id}).explain("executionStats")
            # if obg is COLLSCAN we need an index

            # users
            await self.db.users.create_index("email", unique=True)

            # conversations
            await self.db.conversations.create_index([("session_id", 1), ("timestamp", -1)])

            # otps
            await self.db.otps.create_index("created_at", expireAfterSeconds=600)
            await self.db.otps.create_index("email")

            # Ingested Documents
            #  _id is already unique (stable hash); add compound indexes for fast lookups
            await self.db.ingested_documents.create_index([("symbol", 1), ("published_at", -1)])
            await self.db.ingested_documents.create_index([("symbol", 1), ("type", 1), ("published_at", -1)])
            await self.db.ingested_documents.create_index([("symbol", 1), ("type", 1), ("source", 1)])


database = Database()


async def init_databases():
    await database.connect()


async def close_databases():
    await database.close()


async def create_index():
    await database.create_index()
