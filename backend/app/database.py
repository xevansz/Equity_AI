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

    async def create_index_symbols(self):
        if self.db is not None:
            await self.db.symbols.create_index("_id")  # _id is already unique by default

    async def create_index_symbol_aliases(self):
        if self.db is not None:
            await self.db.symbol_aliases.create_index("normalized_alias", unique=True)
            await self.db.symbol_aliases.create_index([("symbol", 1), ("normalized_alias", 1)], unique=True)

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
    await database.create_index_symbols()
    await database.create_index_symbol_aliases()
    await database.create_index_watchlist()
    await database.create_index_users()
    await database.create_index_conversations()
    await database.create_index_otps()
