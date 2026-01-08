import pytest
from httpx import AsyncClient, ASGITransport
from main import app
from api.dependencies import verify_token

@pytest.fixture
async def client():
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        yield ac

@pytest.mark.asyncio
async def test_create_layout(client):
    payload = {
        "schema_name": "customer",
        "name": "Admin View",
        "definition": [
            {
                "id": "root",
                "type": "row",
                "children": []
            }
        ]
    }
    response = await client.post("/api/v1/layouts/", json=payload)
    assert response.status_code == 201
    data = response.json()
    assert data["name"] == "Admin View"
    assert data["definition"][0]["type"] == "row"

@pytest.mark.asyncio
async def test_resolve_layout(client):
    # 1. Create Default
    await client.post("/api/v1/layouts/", json={
        "schema_name": "customer",
        "name": "Default View",
        "is_default": True,
        "definition": []
    })
    
    # 2. Create Specific
    await client.post("/api/v1/layouts/", json={
        "schema_name": "customer",
        "name": "Sales View",
        "target_group_ids": ["sales_group_id"],
        "definition": []
    })
    
    # 3. Resolve for Sales User
    async def mock_sales_user():
        return {"email": "sales@example.com", "role": "user", "groups": ["sales_group_id"]}
        
    app.dependency_overrides[verify_token] = mock_sales_user
    
    response = await client.get("/api/v1/layouts/resolve/customer")
    assert response.status_code == 200
    data = response.json()
    assert data["name"] == "Sales View"
    
    # 4. Resolve for Other User (should fallback to default)
    async def mock_other_user():
        return {"email": "other@example.com", "role": "user", "groups": ["other_group"]}
    
    app.dependency_overrides[verify_token] = mock_other_user
    
    response = await client.get("/api/v1/layouts/resolve/customer")
    assert response.status_code == 200
    data = response.json()
    assert data["name"] == "Default View"
    
    app.dependency_overrides = {}

@pytest.mark.asyncio
async def test_get_layouts_by_schema(client):
    # Setup: Create 2 layouts
    await client.post("/api/v1/layouts/", json={
        "schema_name": "customer", "name": "L1", "definition": []
    })
    await client.post("/api/v1/layouts/", json={
        "schema_name": "customer", "name": "L2", "definition": []
    })
    
    response = await client.get("/api/v1/layouts/by-schema/customer")
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 2

@pytest.mark.asyncio
async def test_get_layout_by_id(client):
    # Setup
    create_res = await client.post("/api/v1/layouts/", json={
        "schema_name": "customer", "name": "L1", "definition": []
    })
    layout_id = create_res.json()["_id"]
    
    # Test Success
    response = await client.get(f"/api/v1/layouts/{layout_id}")
    assert response.status_code == 200
    assert response.json()["name"] == "L1"
    
    # Test 404
    response = await client.get(f"/api/v1/layouts/{'0'*24}") # Valid ObjectId but missing
    assert response.status_code == 404

@pytest.mark.asyncio
async def test_update_layout(client):
    # Setup
    create_res = await client.post("/api/v1/layouts/", json={
        "schema_name": "customer", "name": "Old", "definition": []
    })
    layout_id = create_res.json()["_id"]
    
    # Test Success
    response = await client.put(f"/api/v1/layouts/{layout_id}", json={
        "name": "New"
    })
    assert response.status_code == 200
    assert response.json()["name"] == "New"
    
    # Test 404
    response = await client.put(f"/api/v1/layouts/{'0'*24}", json={"name": "Ghost"})
    assert response.status_code == 404

@pytest.mark.asyncio
async def test_delete_layout(client):
    # Setup
    create_res = await client.post("/api/v1/layouts/", json={
        "schema_name": "customer", "name": "Temp", "definition": []
    })
    layout_id = create_res.json()["_id"]
    
    # Test Success
    response = await client.delete(f"/api/v1/layouts/{layout_id}")
    assert response.status_code == 200
    
    # Verify Deletion
    get_res = await client.get(f"/api/v1/layouts/{layout_id}")
    assert get_res.status_code == 404
    
    # Test 404 on repeat delete
    response = await client.delete(f"/api/v1/layouts/{layout_id}")
    assert response.status_code == 404
