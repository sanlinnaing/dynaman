import os
import sys
from importlib import reload

# Force APP_MODE to 'all' for tests
os.environ["APP_MODE"] = "all"

import building_blocks.config
reload(building_blocks.config)
from building_blocks.config import settings

import main
reload(main)
from main import app

import pytest
from pymongo import MongoClient
from api.dependencies import verify_token

# Force the database name to be a test database
TEST_DB_NAME = "dynaman_test"
settings.database_name = TEST_DB_NAME

async def mock_verify_token():
    return {"email": "test@example.com", "role": "system_admin"}

@pytest.fixture(scope="function", autouse=True)
def override_auth():
    app.dependency_overrides[verify_token] = mock_verify_token
    yield
    app.dependency_overrides = {}

@pytest.fixture(scope="function", autouse=True)
def clean_db():
    """
    Drops the test database before each test function to ensure a clean state.
    """
    # Use synchronous MongoClient for simplicity in fixture
    # Extract host and port from mongodb_url or just pass the string
    client = MongoClient(settings.mongodb_url)
    
    # Drop the test database
    client.drop_database(TEST_DB_NAME)
    
    yield
    
    # Optional: cleanup after
    # client.drop_database(TEST_DB_NAME)
    client.close()
