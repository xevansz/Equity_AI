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
    print("MongoDB connected")  # TODO: check to see if it really connected to mongodb

  async def close(self):
    if self.client:
      self.client.close()
      print("Mongodb disconnected")

  def get_database(self):
    return self.db

  async def create_index(self):
    if self.db is not None:
      collection = self.db["symbol_cache"]
      await collection.create_index([("company_name", 1)])


database = Database()


async def init_databases():
  await database.connect()


async def close_databases():
  await database.close()


async def create_index_cache():
  await database.create_index()
