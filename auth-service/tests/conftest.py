# Copyright 2024 Google LLC
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     https://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import sys
import os

# Add project root to sys.path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import pytest
from httpx import AsyncClient, ASGITransport
from main import app
from api.dependencies import get_user_repository, get_db
from infrastructure.user_repository import UserRepository
from domain.entities.user import User, UserRole
from domain.services.security_service import SecurityService
from unittest.mock import AsyncMock, MagicMock # Make sure MagicMock is imported

@pytest.fixture
def mock_db():
    return AsyncMock()

# Helper for mocking async iterators
class AsyncIterator:
    def __init__(self, seq):
        self.iter = iter(seq)

    async def __aiter__(self):
        return self

    async def __anext__(self):
        try:
            return next(self.iter)
        except StopIteration:
            raise StopAsyncIteration

# Fixture for tests interacting with FastAPI routers
@pytest.fixture
def mock_repo_for_routers(mock_db):
    return AsyncMock(spec=UserRepository)

# Fixture for unit tests of UserRepository methods
@pytest.fixture
def mock_repo_for_unit_tests(mock_db):
    repo = UserRepository(mock_db)
    repo.collection = MagicMock()
    repo.collection.find_one = AsyncMock()
    repo.collection.find = MagicMock(return_value=AsyncMock())
    repo.collection.insert_one = AsyncMock()
    repo.collection.delete_one = AsyncMock()
    return repo

@pytest.fixture
def override_get_db(mock_db):
    async def _override():
        return mock_db
    return _override

@pytest.fixture
def override_get_user_repo(mock_repo_for_routers): # Use the router-specific mock
    async def _override():
        return mock_repo_for_routers
    return _override

@pytest.fixture
async def client(override_get_db, override_get_user_repo):
    app.dependency_overrides[get_db] = override_get_db
    app.dependency_overrides[get_user_repository] = override_get_user_repo
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        yield ac
    app.dependency_overrides.clear()