import os
from unittest.mock import AsyncMock

import pytest
from httpx import AsyncClient

from ebay_alerts_service.app import api
from ebay_alerts_service.config import Config
from ebay_alerts_service.db import DbConnection

TEST_DB_PATH = "data/db.test.sqlite"
os.environ["APP_DB_PATH"] = TEST_DB_PATH
os.environ["APP_EBAY_API_KEY"] = "123"
os.environ["APP_EBAY_API_URL"] = "https://test.ebay.local"


@pytest.fixture(autouse=True)
async def routine():
    try:
        os.remove(TEST_DB_PATH)
    except FileNotFoundError:
        pass

    config = Config()
    connection = DbConnection(config.db_path)
    await connection.init_schema()
    yield
    os.remove(TEST_DB_PATH)


@pytest.fixture(autouse=False)
async def test_client():
    # when we use FastAPI application with httpx.AsyncClient startup and shutdown events is not triggers
    # so let's call them manually
    await api.router.startup()
    async with AsyncClient(app=api, base_url="http://test.local") as client:
        yield client
    await api.router.shutdown()


@pytest.fixture(autouse=False)
def mock_callbacks():
    api.state.conn.on_create = AsyncMock()
    api.state.conn.on_update = AsyncMock()
    api.state.conn.on_delete = AsyncMock()
    yield


@pytest.fixture(autouse=False)
async def db_connection():
    config = Config()
    connection = DbConnection(config.db_path)
    yield connection
    await connection.close()
