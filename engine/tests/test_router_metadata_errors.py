from fastapi.testclient import TestClient
from unittest.mock import AsyncMock
import pytest
from main import app
from api.dependencies import get_schema_service
from metadata_context.domain.entities.schema import SchemaEntity, FieldDefinition, FieldType

client = TestClient(app)

# Mock Service
mock_service = AsyncMock()

def override_get_service():
    return mock_service

@pytest.fixture(autouse=True)
def setup_overrides():
    app.dependency_overrides[get_schema_service] = override_get_service
    yield
    app.dependency_overrides = {}

def test_create_schema_error():
    mock_service.define_new_entity.side_effect = Exception("Create failed")
    response = client.post("/api/v1/schemas/", json={"entity_name": "ErrorEntity", "fields": []})
    assert response.status_code == 400
    assert response.json()["detail"] == "Create failed"

def test_add_field_error():
    mock_service.add_field_to_entity.side_effect = Exception("Add field failed")
    response = client.post("/api/v1/schemas/TestEntity/fields", json={"name": "f1", "field_type": "string"})
    assert response.status_code == 400
    assert response.json()["detail"] == "Add field failed"

def test_remove_field_error():
    mock_service.remove_field_from_entity.side_effect = Exception("Remove field failed")
    response = client.delete("/api/v1/schemas/TestEntity/fields/f1")
    assert response.status_code == 400
    assert response.json()["detail"] == "Remove field failed"

def test_update_schema_error():
    mock_service.update_entity_schema.side_effect = Exception("Update schema failed")
    response = client.put("/api/v1/schemas/TestEntity", json={"entity_name": "TestEntity", "fields": []})
    assert response.status_code == 400
    assert response.json()["detail"] == "Update schema failed"

def test_partial_update_schema_error():
    mock_service.partial_update_entity_schema.side_effect = Exception("Patch failed")
    response = client.patch("/api/v1/schemas/TestEntity", json={"description": "new"})
    assert response.status_code == 400
    assert response.json()["detail"] == "Patch failed"

def test_update_field_error():
    mock_service.update_field_in_entity.side_effect = Exception("Update field failed")
    response = client.put("/api/v1/schemas/TestEntity/fields/f1", json={"name": "f1", "field_type": "number"})
    assert response.status_code == 400
    assert response.json()["detail"] == "Update field failed"

def test_delete_schema_error():
    mock_service.delete_entity_schema.side_effect = Exception("Delete schema failed")
    response = client.delete("/api/v1/schemas/TestEntity")
    assert response.status_code == 400
    assert response.json()["detail"] == "Delete schema failed"

def test_get_schema_not_found():
    mock_service.get_entity_definition.return_value = None
    response = client.get("/api/v1/schemas/NonExistent")
    assert response.status_code == 404
    assert response.json()["detail"] == "Schema not found"
