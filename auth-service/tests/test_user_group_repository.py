import pytest
from infrastructure.user_group_repository import UserGroupRepository
from domain.entities.user_group import UserGroup
from mongomock_motor import AsyncMongoMockClient
from bson import ObjectId

@pytest.fixture
async def mock_db():
    client = AsyncMongoMockClient()
    db = client["test_db"]
    return db

@pytest.fixture
async def repo(mock_db):
    return UserGroupRepository(mock_db)

@pytest.mark.asyncio
async def test_create_and_get_group(repo):
    group = UserGroup(name="Sales", description="Sales Team")
    created = await repo.create(group)
    assert created.id is not None
    
    fetched = await repo.get_by_id(created.id)
    assert fetched.name == "Sales"
    assert fetched.description == "Sales Team"

@pytest.mark.asyncio
async def test_get_by_name(repo):
    await repo.create(UserGroup(name="Marketing"))
    
    group = await repo.get_by_name("Marketing")
    assert group is not None
    assert group.name == "Marketing"
    
    none_group = await repo.get_by_name("NonExistent")
    assert none_group is None

@pytest.mark.asyncio
async def test_update_group(repo):
    group = await repo.create(UserGroup(name="Dev"))
    
    updated = await repo.update(group.id, {"name": "Engineering", "description": "Tech"})
    assert updated.name == "Engineering"
    assert updated.description == "Tech"
    
    # Verify persistence
    fetched = await repo.get_by_id(group.id)
    assert fetched.name == "Engineering"

    # Update non-existent
    result = await repo.update(str(ObjectId()), {"name": "Ghost"})
    assert result is None

@pytest.mark.asyncio
async def test_delete_group(repo):
    group = await repo.create(UserGroup(name="Temp"))
    
    success = await repo.delete(group.id)
    assert success is True
    
    fetched = await repo.get_by_id(group.id)
    assert fetched is None
    
    # Delete non-existent
    success = await repo.delete(str(ObjectId()))
    assert success is False

@pytest.mark.asyncio
async def test_get_all(repo):
    await repo.create(UserGroup(name="A"))
    await repo.create(UserGroup(name="B"))
    
    groups = await repo.get_all()
    assert len(groups) == 2
    names = sorted([g.name for g in groups])
    assert names == ["A", "B"]

@pytest.mark.asyncio
async def test_invalid_id_handling(repo):
    assert await repo.get_by_id("invalid-oid") is None
    assert await repo.update("invalid-oid", {}) is None
    assert await repo.delete("invalid-oid") is False
