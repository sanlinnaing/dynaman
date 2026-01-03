import pytest
from httpx import AsyncClient
from domain.entities.user import User, UserRole
from domain.services.security_service import SecurityService
from unittest.mock import AsyncMock

@pytest.mark.anyio
async def test_health_check(client: AsyncClient):
    response = await client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}

@pytest.mark.anyio
async def test_login_success(client: AsyncClient, mock_repo_for_routers: AsyncMock):
    password = "password123"
    hashed_password = SecurityService.get_password_hash(password)
    user = User(
        email="test@example.com",
        hashed_password=hashed_password,
        role=UserRole.USER,
        _id="user123"
    )
    
    mock_repo_for_routers.get_by_email.return_value = user

    response = await client.post(
        "/api/v1/auth/token",
        data={"username": "test@example.com", "password": password},
        headers={"content-type": "application/x-www-form-urlencoded"}
    )
    
    assert response.status_code == 200
    data = response.json()
    assert "access_token" in data
    assert data["token_type"] == "bearer"
    mock_repo_for_routers.get_by_email.assert_called_once_with("test@example.com")


@pytest.mark.anyio
async def test_login_failure(client: AsyncClient, mock_repo_for_routers: AsyncMock):
    mock_repo_for_routers.get_by_email.return_value = None

    response = await client.post(
        "/api/v1/auth/token",
        data={"username": "wrong@example.com", "password": "password"},
        headers={"content-type": "application/x-www-form-urlencoded"}
    )
    
    assert response.status_code == 401
    mock_repo_for_routers.get_by_email.assert_called_once_with("wrong@example.com")