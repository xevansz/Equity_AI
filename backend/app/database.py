"""Database Initialization"""

from motor.motor_asyncio import AsyncIOMotorClient, AsyncIOMotorDatabase
from pymongo.errors import PyMongoError

from app.config import settings
from app.exceptions import DatabaseError
from app.logging_config import get_logger

logger = get_logger(__name__)


class Database:
    """Database connection manager for MongoDB."""

    def __init__(self) -> None:
        """Initialize database connection manager."""
        self.client: AsyncIOMotorClient | None = None
        self.db: AsyncIOMotorDatabase | None = None

    async def connect(self) -> None:
        """Connect to MongoDB database.

        Raises:
            DatabaseError: If connection fails
        """
        try:
            self.client = AsyncIOMotorClient(settings.MONGODB_URI, serverSelectionTimeoutMS=5000)
            self.db = self.client[settings.DB_NAME]

            await self.client.admin.command("ping")

            logger.info("MongoDB connected successfully")

        except PyMongoError as e:
            logger.exception("MongoDB connection failed")
            raise DatabaseError(
                "Failed to connect to MongoDB", details={"uri": settings.MONGODB_URI, "error": str(e)}
            ) from e

    async def close(self) -> None:
        """Close database connection."""
        if self.client:
            self.client.close()
            logger.info("MongoDB disconnected")

    def get_database(self) -> AsyncIOMotorDatabase | None:
        """Get database instance.

        Returns:
            Database instance or None if not connected
        """
        return self.db

    async def create_index(self) -> None:
        """Create database indexes for optimal query performance.

        Raises:
            DatabaseError: If index creation fails
        """
        if self.db is None:
            raise DatabaseError("Database not connected")

        try:
            await self.db.watchlist.create_index("user_id")

            # symbol resolver
            await self.db.symbol_aliases.create_index("normalized_alias", unique=True)
            await self.db.symbol_aliases.create_index([("symbol", 1), ("normalized_alias", 1)], unique=True)

            # Watchlist
            await self.db.watchlist.create_index([("user_id", 1), ("symbol", 1)], unique=True)

            # users
            await self.db.users.create_index("email", unique=True)

            # conversations
            await self.db.conversations.create_index([("session_id", 1), ("timestamp", -1)])

            # otps
            await self.db.otps.create_index("created_at", expireAfterSeconds=600)
            await self.db.otps.create_index("email")

            # Ingested Documents
            await self.db.ingested_documents.create_index([("symbol", 1), ("published_at", -1)])
            await self.db.ingested_documents.create_index([("symbol", 1), ("type", 1), ("published_at", -1)])
            await self.db.ingested_documents.create_index([("symbol", 1), ("type", 1), ("source", 1)])

            logger.info("Database indexes created successfully")
        except PyMongoError as e:
            logger.exception("Failed to create database indexes")
            raise DatabaseError("Failed to create database indexes", details={"error": str(e)}) from e


database = Database()


async def init_databases():
    await database.connect()


async def close_databases():
    await database.close()


async def create_index():
    await database.create_index()
