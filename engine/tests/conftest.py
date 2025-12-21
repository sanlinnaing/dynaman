import pytest
from pymongo import MongoClient
from building_blocks.config import settings

# Force the database name to be a test database
TEST_DB_NAME = "dynaman_test"
settings.database_name = TEST_DB_NAME

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
