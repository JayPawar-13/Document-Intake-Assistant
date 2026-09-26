import logging
from motor.motor_asyncio import AsyncIOMotorClient, AsyncIOMotorDatabase
from app.config import settings
from typing import Optional

logger = logging.getLogger(__name__)

class MongoDBManager:
    client: Optional[AsyncIOMotorClient] = None
    db: Optional[AsyncIOMotorDatabase] = None

    async def connect(self):
        """Initialize connection to MongoDB"""
        try:
            logger.info(f"Connecting to MongoDB at {settings.MONGODB_URI}...")
            self.client = AsyncIOMotorClient(
                settings.MONGODB_URI,
                serverSelectionTimeoutMS=5000,
                connectTimeoutMS=5000
            )
            self.db = self.client[settings.MONGODB_DATABASE]
            # Verify connectivity
            await self.client.admin.command("ping")
            logger.info(f"Successfully connected to MongoDB database: {settings.MONGODB_DATABASE}")

            # Ensure indexes
            await self._create_indexes()
        except Exception as e:
            logger.error(f"Failed to connect to MongoDB: {e}")
            raise e

    async def _create_indexes(self):
        """Create necessary indexes for efficient querying"""
        if self.db is None:
            return
        try:
            # Index on session_id for conversations
            await self.db.conversations.create_index("session_id")
            # Index on session_id for structured_states
            await self.db.structured_states.create_index("session_id", unique=True)
            # Index on session_id for documents
            await self.db.documents.create_index("session_id", unique=True)
            logger.info("MongoDB indexes verified.")
        except Exception as e:
            logger.warning(f"Index creation warning: {e}")

    async def disconnect(self):
        """Close MongoDB connection"""
        if self.client:
            self.client.close()
            logger.info("Closed MongoDB connection.")

    async def ping(self) -> bool:
        """Check if MongoDB is reachable"""
        if not self.client:
            return False
        try:
            await self.client.admin.command("ping")
            return True
        except Exception:
            return False

    @property
    def sessions(self):
        return self.db["sessions"]

    @property
    def conversations(self):
        return self.db["conversations"]

    @property
    def structured_states(self):
        return self.db["structured_states"]

    @property
    def documents(self):
        return self.db["documents"]


db_manager = MongoDBManager()


async def get_db() -> AsyncIOMotorDatabase:
    if db_manager.db is None:
        await db_manager.connect()
    return db_manager.db
