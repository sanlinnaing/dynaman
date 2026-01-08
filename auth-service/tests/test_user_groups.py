import pytest
from httpx import AsyncClient
from unittest.mock import AsyncMock
from domain.entities.user import User, UserRole
from domain.entities.user_group import UserGroup
from api.dependencies import get_user_group_repository, get_current_user
from main import app

@pytest.fixture
def mock_group_repo():
    return AsyncMock()

@pytest.fixture
def system_admin_user():
    return User(
        email="admin@example.com",
        hashed_password="hash",
        role=UserRole.SYSTEM_ADMIN,
        group_ids=[]
    )

@pytest.mark.asyncio
async def test_create_group(client, mock_group_repo, system_admin_user):
    app.dependency_overrides[get_user_group_repository] = lambda: mock_group_repo
    app.dependency_overrides[get_current_user] = lambda: system_admin_user

    mock_group_repo.get_by_name.return_value = None
    # Simulate create returning the object
    async def create_side_effect(group):
        group.id = "mock_id"
        return group
    mock_group_repo.create.side_effect = create_side_effect

    response = await client.post("/api/v1/groups", json={
        "name": "Sales",
        "description": "Sales Team"
    })

    assert response.status_code == 201
    data = response.json()
    assert data["name"] == "Sales"
    assert data["description"] == "Sales Team"
    assert "_id" in data # Aliased id
    
    app.dependency_overrides.clear()

@pytest.mark.asyncio
async def test_list_groups(client, mock_group_repo, system_admin_user):
    app.dependency_overrides[get_user_group_repository] = lambda: mock_group_repo
    app.dependency_overrides[get_current_user] = lambda: system_admin_user

    mock_group_repo.get_all.return_value = [
        UserGroup(id="1", name="G1"),
        UserGroup(id="2", name="G2")
    ]

    response = await client.get("/api/v1/groups")
    assert response.status_code == 200
    assert len(response.json()) == 2
    
    app.dependency_overrides.clear()

@pytest.mark.asyncio
async def test_get_group_by_id(client, mock_group_repo, system_admin_user):
    app.dependency_overrides[get_user_group_repository] = lambda: mock_group_repo
    app.dependency_overrides[get_current_user] = lambda: system_admin_user

    mock_group = UserGroup(id="123", name="G1")
    mock_group_repo.get_by_id.return_value = mock_group

    response = await client.get("/api/v1/groups/123")
    assert response.status_code == 200
    assert response.json()["name"] == "G1"

    mock_group_repo.get_by_id.return_value = None
    response = await client.get("/api/v1/groups/999")
    assert response.status_code == 404

    app.dependency_overrides.clear()

@pytest.mark.asyncio
async def test_update_group(client, mock_group_repo, system_admin_user):
    app.dependency_overrides[get_user_group_repository] = lambda: mock_group_repo
    app.dependency_overrides[get_current_user] = lambda: system_admin_user

    updated_group = UserGroup(id="123", name="Updated Name")
    mock_group_repo.update.return_value = updated_group

    response = await client.put("/api/v1/groups/123", json={"name": "Updated Name"})
    assert response.status_code == 200
    assert response.json()["name"] == "Updated Name"

    mock_group_repo.update.return_value = None
    response = await client.put("/api/v1/groups/999", json={"name": "Ghost"})
    assert response.status_code == 404

    app.dependency_overrides.clear()

@pytest.mark.asyncio
async def test_delete_group(client, mock_group_repo, system_admin_user):
    app.dependency_overrides[get_user_group_repository] = lambda: mock_group_repo
    app.dependency_overrides[get_current_user] = lambda: system_admin_user

    mock_group_repo.delete.return_value = True
    response = await client.delete("/api/v1/groups/123")
    assert response.status_code == 200

    mock_group_repo.delete.return_value = False
    response = await client.delete("/api/v1/groups/999")
    assert response.status_code == 404

    app.dependency_overrides.clear()

@pytest.mark.asyncio
async def test_create_duplicate_group(client, mock_group_repo, system_admin_user):
    app.dependency_overrides[get_user_group_repository] = lambda: mock_group_repo
    app.dependency_overrides[get_current_user] = lambda: system_admin_user

    mock_group_repo.get_by_name.return_value = UserGroup(id="1", name="Sales")
    
    response = await client.post("/api/v1/groups", json={"name": "Sales"})
    assert response.status_code == 400
    
    app.dependency_overrides.clear()
