import pytest
from httpx import AsyncClient
from domain.entities.user import User, UserRole
from domain.services.security_service import SecurityService
from bson import ObjectId
from unittest.mock import AsyncMock, MagicMock # Import MagicMock for return values

@pytest.mark.anyio
async def test_delete_user_success(client: AsyncClient, mock_repo_for_routers: AsyncMock):
    # Setup Current User (User Admin)
    admin_user = User(
        email="admin@example.com",
        hashed_password="hashed",
        role=UserRole.USER_ADMIN,
        _id="admin123"
    )
    
    # Setup Target User (User)
    target_user = User(
        email="target@example.com",
        hashed_password="hashed",
        role=UserRole.USER,
        _id="target123"
    )

    # Mock get_by_email for get_current_user
    mock_repo_for_routers.get_by_email.return_value = admin_user
    
    # Mock get_by_id for finding target user
    mock_repo_for_routers.get_by_id.return_value = target_user
    
    # Mock delete
    mock_repo_for_routers.delete.return_value = True

    # Create Token for Admin
    token = SecurityService.create_access_token(data={"sub": admin_user.email, "role": admin_user.role})
    headers = {"Authorization": f"Bearer {token}"}

    response = await client.delete("/api/v1/auth/users/target123", headers=headers)
    
    assert response.status_code == 200
    assert response.json() == {"message": "User deleted successfully"}
    
    # Verify get_by_id was called
    mock_repo_for_routers.get_by_id.assert_called_with("target123")
    mock_repo_for_routers.delete.assert_called_once_with("target123")

@pytest.mark.anyio
async def test_delete_system_admin_by_user_admin_forbidden(client: AsyncClient, mock_repo_for_routers: AsyncMock):
    # Setup Current User (User Admin)
    admin_user = User(
        email="admin@example.com",
        hashed_password="hashed",
        role=UserRole.USER_ADMIN,
        _id="admin123"
    )
    
    # Setup Target User (System Admin)
    target_user = User(
        email="sysadmin@example.com",
        hashed_password="hashed",
        role=UserRole.SYSTEM_ADMIN,
        _id="sysadmin123"
    )

    mock_repo_for_routers.get_by_email.return_value = admin_user
    mock_repo_for_routers.get_by_id.return_value = target_user

    token = SecurityService.create_access_token(data={"sub": admin_user.email, "role": admin_user.role})
    headers = {"Authorization": f"Bearer {token}"}

    response = await client.delete("/api/v1/auth/users/sysadmin123", headers=headers)
    
    assert response.status_code == 403
    assert response.json()["detail"] == "User Admins cannot delete System Admins"
    mock_repo_for_routers.get_by_id.assert_called_once_with("sysadmin123")
    mock_repo_for_routers.delete.assert_not_called()

@pytest.mark.anyio
async def test_delete_user_not_found(client: AsyncClient, mock_repo_for_routers: AsyncMock):
    # Setup Current User (System Admin)
    admin_user = User(
        email="sysadmin@example.com",
        hashed_password="hashed",
        role=UserRole.SYSTEM_ADMIN,
        _id="sysadmin123"
    )

    mock_repo_for_routers.get_by_email.return_value = admin_user
    mock_repo_for_routers.get_by_id.return_value = None # Target not found
    mock_repo_for_routers.delete.return_value = False # Explicitly mock delete's return value for robustness

    token = SecurityService.create_access_token(data={"sub": admin_user.email, "role": admin_user.role})
    headers = {"Authorization": f"Bearer {token}"}

    response = await client.delete("/api/v1/auth/users/nonexistent", headers=headers)
    
    assert response.status_code == 404
    assert response.json()["detail"] == "User not found"
    mock_repo_for_routers.get_by_id.assert_called_once_with("nonexistent")
    mock_repo_for_routers.delete.assert_not_called() # Delete should not be called if user not found

# --- New tests for UserRepository coverage ---

@pytest.mark.anyio
async def test_user_repo_get_by_email_not_found(mock_repo_for_unit_tests: AsyncMock):
    # For user repo unit tests, mock the collection methods directly
    mock_repo_for_unit_tests.collection.find_one.return_value = None
    user = await mock_repo_for_unit_tests.get_by_email("nonexistent@example.com")
    assert user is None
    mock_repo_for_unit_tests.collection.find_one.assert_called_once_with({"email": "nonexistent@example.com"})

@pytest.mark.anyio
async def test_user_repo_get_by_email_found(mock_repo_for_unit_tests: AsyncMock):
    user_doc = {"_id": ObjectId(), "email": "exists@example.com", "hashed_password": "hashed", "is_active": True, "role": "user", "provider": "local"}
    mock_repo_for_unit_tests.collection.find_one.return_value = user_doc
    user = await mock_repo_for_unit_tests.get_by_email("exists@example.com")
    assert user is not None
    assert user.email == "exists@example.com"
    mock_repo_for_unit_tests.collection.find_one.assert_called_once_with({"email": "exists@example.com"})


@pytest.mark.anyio
async def test_user_repo_get_by_id_invalid_id(mock_repo_for_unit_tests: AsyncMock):
    user = await mock_repo_for_unit_tests.get_by_id("invalid_id_string")
    assert user is None
    mock_repo_for_unit_tests.collection.find_one.assert_not_called() # Should not try to query with invalid ID

@pytest.mark.anyio
async def test_user_repo_get_by_id_not_found(mock_repo_for_unit_tests: AsyncMock):
    mock_repo_for_unit_tests.collection.find_one.return_value = None
    test_id = str(ObjectId())
    user = await mock_repo_for_unit_tests.get_by_id(test_id) # Use a valid but non-existent ObjectId
    assert user is None
    mock_repo_for_unit_tests.collection.find_one.assert_called_once_with({"_id": ObjectId(test_id)})


@pytest.mark.anyio
async def test_user_repo_get_by_id_found(mock_repo_for_unit_tests: AsyncMock):
    test_id = str(ObjectId())
    user_doc = {"_id": ObjectId(test_id), "email": "exists@example.com", "hashed_password": "hashed", "is_active": True, "role": "user", "provider": "local"}
    mock_repo_for_unit_tests.collection.find_one.return_value = user_doc
    user = await mock_repo_for_unit_tests.get_by_id(test_id)
    assert user is not None
    assert user.id == test_id
    mock_repo_for_unit_tests.collection.find_one.assert_called_once_with({"_id": ObjectId(test_id)})


@pytest.mark.anyio
async def test_user_repo_create_user(mock_repo_for_unit_tests: AsyncMock):
    new_user_data = User(email="new@example.com", hashed_password="hashed", role=UserRole.USER)
    inserted_id = ObjectId()
    # Mock insert_one to return an object with inserted_id
    mock_repo_for_unit_tests.collection.insert_one.return_value = MagicMock(inserted_id=inserted_id)

    created_user = await mock_repo_for_unit_tests.create(new_user_data)
    assert created_user.id == str(inserted_id)
    mock_repo_for_unit_tests.collection.insert_one.assert_called_once()
    # Also assert that the model_dump was called correctly
    expected_user_dict = new_user_data.model_dump(by_alias=True, exclude={"id"})
    mock_repo_for_unit_tests.collection.insert_one.assert_called_once_with(expected_user_dict)


@pytest.mark.anyio
async def test_user_repo_get_all_empty(mock_repo_for_unit_tests: AsyncMock):
    # Mock the async iterator behavior for an empty cursor
    mock_repo_for_unit_tests.collection.find.return_value.__aiter__.return_value = []
    
    users = await mock_repo_for_unit_tests.get_all()
    assert users == []
    mock_repo_for_unit_tests.collection.find.assert_called_once()

@pytest.mark.anyio
async def test_user_repo_get_all_with_users(mock_repo_for_unit_tests: AsyncMock):
    user1_doc = {"_id": ObjectId(), "email": "u1@e.com", "hashed_password": "h1", "is_active": True, "role": "user", "provider": "local"}
    user2_doc = {"_id": ObjectId(), "email": "u2@e.com", "hashed_password": "h2", "is_active": True, "role": "user_admin", "provider": "local"}
    
    # Mock the async iterator behavior with two user documents
    mock_repo_for_unit_tests.collection.find.return_value.__aiter__.return_value = [user1_doc, user2_doc]
    
    users = await mock_repo_for_unit_tests.get_all()
    assert len(users) == 2
    assert users[0].email == user1_doc["email"]
    assert users[1].email == user2_doc["email"]
    mock_repo_for_unit_tests.collection.find.assert_called_once()

@pytest.mark.anyio
async def test_user_repo_delete_user_success(mock_repo_for_unit_tests: AsyncMock):
    mock_repo_for_unit_tests.collection.delete_one.return_value = MagicMock(deleted_count=1)
    success = await mock_repo_for_unit_tests.delete(str(ObjectId()))
    assert success is True
    mock_repo_for_unit_tests.collection.delete_one.assert_called_once()

@pytest.mark.anyio
async def test_user_repo_delete_user_not_found_valid_id(mock_repo_for_unit_tests: AsyncMock):
    mock_repo_for_unit_tests.collection.delete_one.return_value = MagicMock(deleted_count=0)
    success = await mock_repo_for_unit_tests.delete(str(ObjectId()))
    assert success is False
    mock_repo_for_unit_tests.collection.delete_one.assert_called_once()