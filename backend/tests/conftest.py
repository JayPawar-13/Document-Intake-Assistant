import pytest
import pytest_asyncio
import sys
import os

# Ensure backend folder is in sys.path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from app.database.mongodb import db_manager
from httpx import AsyncClient, ASGITransport
from app.main import app


@pytest_asyncio.fixture(autouse=True)
async def setup_test_db():
    """Connect to test MongoDB on the active test event loop"""
    await db_manager.connect()
    yield
    # Keep client clean


@pytest_asyncio.fixture
async def async_client():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        yield client
