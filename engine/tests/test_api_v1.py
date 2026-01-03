from fastapi.testclient import TestClient
from unittest.mock import AsyncMock, MagicMock
import pytest
from main import app
from api.dependencies import get_record_use_case, get_schema_service, verify_token
from building_blocks.errors import DomainError

client = TestClient(app)

# Mocks
mock_record_use_case = AsyncMock()
mock_schema_service = AsyncMock()

async def mock_verify_token():
    return {"email": "test@example.com", "role": "system_admin"}

def override_get_record_use_case():
    return mock_record_use_case

def override_get_schema_service():
    return mock_schema_service

@pytest.fixture(autouse=True)
def setup_overrides():
    app.dependency_overrides[get_record_use_case] = override_get_record_use_case
    app.dependency_overrides[get_schema_service] = override_get_schema_service
    app.dependency_overrides[verify_token] = mock_verify_token
    yield
    app.dependency_overrides = {}

# --- Execution Router Tests ---

def test_add_data_success():
    mock_record_use_case.create_new_record.return_value = "new_id_123"
    response = client.post("/api/v1/data/TestEntity", json={"field": "value"})
    assert response.status_code == 200
    assert response.json() == {"id": "new_id_123", "status": "success"}

def test_add_data_domain_error():
    mock_record_use_case.create_new_record.side_effect = DomainError("Invalid data", errors=[{"field": "test_field", "issue": "test_issue", "detail": "Too long"}])
    response = client.post("/api/v1/data/TestEntity", json={"field": "value"})
    assert response.status_code == 400
    assert response.json()["message"] == "Invalid data"

def test_list_data_success():
    mock_record_use_case.list_records.return_value = [{"id": "1", "data": "A"}]
    response = client.get("/api/v1/data/TestEntity?page=1")
    assert response.status_code == 200
    assert response.json() == [{"id": "1", "data": "A"}]

def test_get_record_success():
    mock_record_use_case.get_record.return_value = {"id": "1", "data": "A"}
    response = client.get("/api/v1/data/TestEntity/1")
    assert response.status_code == 200
    assert response.json() == {"id": "1", "data": "A"}

def test_get_record_not_found():
    mock_record_use_case.get_record.return_value = None
    response = client.get("/api/v1/data/TestEntity/999")
    assert response.status_code == 404

def test_update_record_success():
    mock_record_use_case.update_record.return_value = True
    response = client.put("/api/v1/data/TestEntity/1", json={"field": "new_val"})
    assert response.status_code == 200
    assert response.json()["status"] == "updated"

def test_delete_record_success():
    mock_record_use_case.delete_record.return_value = True
    response = client.delete("/api/v1/data/TestEntity/1")
    assert response.status_code == 200
    assert response.json()["status"] == "deleted"

# --- Metadata Router Tests ---

def test_create_schema_success():
    mock_schema_service.define_new_entity.return_value = "NewEntity"
    response = client.post("/api/v1/schemas/", json={"entity_name": "NewEntity", "fields": []})
    assert response.status_code == 200
    assert response.json() == {"message": "Entity 'NewEntity' created successfully"}

def test_get_schema_success():
    mock_schema_service.get_entity_definition.return_value = {"entity_name": "TestEntity", "fields": []}
    response = client.get("/api/v1/schemas/TestEntity")
    assert response.status_code == 200
    assert response.json() == {"entity_name": "TestEntity", "fields": []}

def test_get_all_schemas_success():
    mock_schema_service.list_all_entities.return_value = ["EntityA", "EntityB"]
    response = client.get("/api/v1/schemas/")
    assert response.status_code == 200
    assert response.json() == ["EntityA", "EntityB"]

def test_add_field_success():
    mock_schema_service.add_field_to_entity.return_value = "Field added"
    response = client.post("/api/v1/schemas/TestEntity/fields", json={"name": "new_field", "field_type": "string"})
    assert response.status_code == 200
    assert response.json() == {"message": "Field added"}

def test_update_field_success():
    mock_schema_service.update_field_in_entity.return_value = "Field updated"
    # Note: The route is PUT /{name}/fields/{field_name}
    response = client.put("/api/v1/schemas/TestEntity/fields/existing_field", json={"name": "existing_field", "field_type": "number"})
    assert response.status_code == 200
    assert response.json() == {"message": "Field updated"}
