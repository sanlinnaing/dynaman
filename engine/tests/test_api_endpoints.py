import pytest
import json
import os
from fastapi.testclient import TestClient
from main import app

def load_payloads():
    payload_path = os.path.join(os.path.dirname(__file__), "test_payloads.json")
    with open(payload_path, "r") as f:
        return json.load(f)

DATA = load_payloads()

def test_api_integration_flow():
    """
    Executes the integration flow defined in test_payloads.json.
    """
    with TestClient(app) as client:
        # --- 1. Metadata Context (Schemas) ---
        
        # 1. Create Schema
        schema_test = DATA["metadata_context"]["create_schema"]
        url = schema_test["endpoint"].split(" ")[1]
        response = client.post(url, json=schema_test["payload"])
        assert response.status_code == 200, f"Create Schema failed: {response.text}"
        
        # 2. Add Field
        add_field_test = DATA["metadata_context"]["add_field"]
        url = add_field_test["endpoint"].split(" ")[1]
        response = client.post(url, json=add_field_test["payload"])
        assert response.status_code == 200, f"Add Field failed: {response.text}"
        
        # 3. Update Field
        update_field_test = DATA["metadata_context"]["update_field"]
        url = update_field_test["endpoint"].split(" ")[1]
        response = client.put(url, json=update_field_test["payload"])
        assert response.status_code == 200, f"Update Field failed: {response.text}"
        
        # 4. Partial Update Schema
        patch_schema_test = DATA["metadata_context"]["partial_update_schema"]
        url = patch_schema_test["endpoint"].split(" ")[1]
        response = client.patch(url, json=patch_schema_test["payload"])
        assert response.status_code == 200, f"Partial Update Schema failed: {response.text}"
        
        # --- 2. Execution Context (Records) ---
        
        # 1. Create Record
        create_record_test = DATA["execution_context"]["create_record"]
        url = create_record_test["endpoint"].split(" ")[1]
        response = client.post(url, json=create_record_test["payload"])
        assert response.status_code == 200, f"Create Record failed: {response.text}"
        
        record_id = response.json().get("id")
        assert record_id is not None, "Record ID not returned"
        
        # 2. Update Record
        update_record_test = DATA["execution_context"]["update_record"]
        endpoint_template = update_record_test["endpoint"].split(" ")[1]
        url = endpoint_template.replace("{record_id}", record_id)
        response = client.put(url, json=update_record_test["payload"])
        assert response.status_code == 200, f"Update Record failed: {response.text}"
        
        # 3. Delete Record
        delete_record_test = DATA["execution_context"]["delete_record"]
        endpoint_template = delete_record_test["endpoint"].split(" ")[1]
        url = endpoint_template.replace("{record_id}", record_id)
        response = client.delete(url)
        assert response.status_code == 200, f"Delete Record failed: {response.text}"
        
        # 4. Verify Soft Delete
        url = f"/data/Product/{record_id}"
        response = client.get(url)
        # Depending on implementation, soft deleted might be 404 or return with deleted flag.
        # Previous script expected 404.
        assert response.status_code == 404, f"Soft deleted record should return 404, got {response.status_code}"
        
        # 5. Test Unique Constraint (Duplicate Record)
        duplicate_record_test = DATA["execution_context"]["duplicate_record"]
        
        # Re-create the original record first to have a conflict (since we deleted it)
        create_record_test = DATA["execution_context"]["create_record"]
        url = create_record_test["endpoint"].split(" ")[1]
        client.post(url, json=create_record_test["payload"]) # Re-create
        
        # Now try to create duplicate
        url = duplicate_record_test["endpoint"].split(" ")[1]
        response = client.post(url, json=duplicate_record_test["payload"])
        # Expecting failure due to unique constraint on 'sku'
        # The original script expected 400
        assert response.status_code == 400, f"Duplicate record creation should fail with 400, got {response.status_code}"
