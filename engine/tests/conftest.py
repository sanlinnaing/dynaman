import os
import sys
from importlib import reload
from unittest.mock import MagicMock

# Force APP_MODE to 'all' for tests
os.environ["APP_MODE"] = "all"

import building_blocks.config
reload(building_blocks.config)
from building_blocks.config import settings

import main
reload(main)
from main import app

import pytest
from api.dependencies import verify_token
import api.dependencies

# Force the database name to be a test database
TEST_DB_NAME = "dynaman_test"
settings.database_name = TEST_DB_NAME

# Try importing mongomock_motor, fallback to standard if missing (though we added it)
try:
    from mongomock_motor import AsyncMongoMockClient
except ImportError:
    AsyncMongoMockClient = None

async def mock_verify_token():
    return {"email": "test@example.com", "role": "system_admin"}

@pytest.fixture(scope="function", autouse=True)
def override_auth():
    app.dependency_overrides[verify_token] = mock_verify_token
    yield
    app.dependency_overrides = {}

@pytest.fixture(scope="function", autouse=True)
def mock_mongo(monkeypatch):
    """
    Patches the engine.api.dependencies database connection with mongomock-motor.
    This runs for every test, ensuring a fresh in-memory database.
    """
    if not AsyncMongoMockClient:
        pytest.fail("mongomock-motor is not installed")

    # Create Mock Client
    mock_client = AsyncMongoMockClient()
    mock_db = mock_client[TEST_DB_NAME]

    # Patch the global variables in api.dependencies
    monkeypatch.setattr(api.dependencies, "client", mock_client)
    monkeypatch.setattr(api.dependencies, "db", mock_db)

    # Patch connect_db to do nothing (or ensure it uses our mock)
    def mock_connect_db():
        api.dependencies.client = mock_client
        api.dependencies.db = mock_db
        
    monkeypatch.setattr(api.dependencies, "connect_db", mock_connect_db)

    # Ensure clean state: Drop database before test
    # Since AsyncMongoMockClient is async, we can't block easily in a sync fixture without loop.
    # However, mongomock starts fresh for each new client instance usually, 
    # OR we can just rely on the fact it's a new object if we create it here.
    # But AsyncMongoMockClient might share state if not careful? 
    # Usually instantiating a new AsyncMongoMockClient() is enough for a clean slate.
    
    yield mock_client

    # Cleanup
    mock_client.close()