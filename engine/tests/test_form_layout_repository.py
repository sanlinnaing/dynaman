import pytest
from metadata_context.infrastructure.form_layout_repository import FormLayoutRepository
from metadata_context.domain.entities.form_layout import FormLayout
from mongomock_motor import AsyncMongoMockClient
from bson import ObjectId

@pytest.fixture
async def mock_db():
    client = AsyncMongoMockClient()
    db = client["test_engine_db"]
    return db

@pytest.fixture
async def repo(mock_db):
    return FormLayoutRepository(mock_db)

@pytest.mark.asyncio
async def test_create_and_get_layout(repo):
    layout = FormLayout(
        schema_name="customer",
        name="Admin View",
        definition=[{"id": "1", "type": "row"}]
    )
    created = await repo.create(layout)
    assert created.id is not None
    
    fetched = await repo.get_by_id(created.id)
    assert fetched.name == "Admin View"
    assert fetched.schema_name == "customer"

@pytest.mark.asyncio
async def test_get_by_schema(repo):
    await repo.create(FormLayout(schema_name="customer", name="View 1", definition=[]))
    await repo.create(FormLayout(schema_name="customer", name="View 2", definition=[]))
    await repo.create(FormLayout(schema_name="order", name="Order View", definition=[]))
    
    layouts = await repo.get_by_schema("customer")
    assert len(layouts) == 2
    names = sorted([l.name for l in layouts])
    assert names == ["View 1", "View 2"]

@pytest.mark.asyncio
async def test_update_layout(repo):
    layout = await repo.create(FormLayout(schema_name="customer", name="Old Name", definition=[]))
    
    updated = await repo.update(layout.id, {"name": "New Name"})
    assert updated.name == "New Name"
    
    fetched = await repo.get_by_id(layout.id)
    assert fetched.name == "New Name"
    
    # Update non-existent
    assert await repo.update(str(ObjectId()), {}) is None

@pytest.mark.asyncio
async def test_delete_layout(repo):
    layout = await repo.create(FormLayout(schema_name="customer", name="Temp", definition=[]))
    
    success = await repo.delete(layout.id)
    assert success is True
    
    assert await repo.get_by_id(layout.id) is None
    assert await repo.delete(str(ObjectId())) is False

@pytest.mark.asyncio
async def test_invalid_id_handling(repo):
    assert await repo.get_by_id("invalid-oid") is None
    assert await repo.update("invalid-oid", {}) is None
    assert await repo.delete("invalid-oid") is False
