import pytest
from httpx import AsyncClient, ASGITransport
from main import app
from api.dependencies import verify_token

@pytest.fixture
async def client():
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        yield ac

@pytest.mark.asyncio
async def test_create_layout_with_properties(client):
    """Test that extended properties (required, readOnly, etc.) are stored correctly"""
    payload = {
        "schema_name": "customer_extended",
        "name": "Property Test View",
        "definition": [
            {
                "id": "field-1",
                "type": "field",
                "label": "Email",
                "fieldName": "email",
                "fieldType": "email",
                "required": True,
                "readOnly": True,
                "placeholder": "Enter email here",
                "helperText": "We will not spam you"
            }
        ]
    }
    response = await client.post("/api/v1/layouts/", json=payload)
    assert response.status_code == 201
    data = response.json()
    
    item = data["definition"][0]
    assert item["required"] is True
    assert item["readOnly"] is True
    assert item["placeholder"] == "Enter email here"
    assert item["helperText"] == "We will not spam you"

@pytest.mark.asyncio
async def test_update_layout_with_properties(client):
    # 1. Create initial layout
    create_res = await client.post("/api/v1/layouts/", json={
        "schema_name": "customer_extended",
        "name": "Update Test",
        "definition": [
            {
                "id": "field-1",
                "type": "field",
                "label": "Name",
                "fieldName": "name"
            }
        ]
    })
    layout_id = create_res.json()["_id"]

    # 2. Update with properties
    update_payload = {
        "definition": [
            {
                "id": "field-1",
                "type": "field",
                "label": "Name",
                "fieldName": "name",
                "required": True,
                "helperText": "Updated helper"
            }
        ]
    }
    
    response = await client.put(f"/api/v1/layouts/{layout_id}", json=update_payload)
    assert response.status_code == 200
    data = response.json()
    
    item = data["definition"][0]
    assert item["required"] is True
    assert item["helperText"] == "Updated helper"
