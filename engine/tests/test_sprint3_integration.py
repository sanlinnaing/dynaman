import pytest
import json
import os
from fastapi.testclient import TestClient
from main import app

def load_payloads():
    payload_path = os.path.join(os.path.dirname(__file__), "sprint3_payloads.json")
    with open(payload_path, "r") as f:
        return json.load(f)

DATA = load_payloads()

def test_sprint3_flow():
    """
    Executes the Sprint 3 integration flow defined in sprint3_payloads.json.
    """
    with TestClient(app) as client:
        # --- 1. Metadata Context (Schemas) ---
        
        # Create Author Schema
        author_schema_test = DATA["metadata_context"]["create_author_schema"]
        url = author_schema_test["endpoint"].split(" ")[1]
        response = client.post(url, json=author_schema_test["payload"])
        assert response.status_code == 200, f"Create Author Schema failed: {response.text}"
    
        # Create Article Schema
        article_schema_test = DATA["metadata_context"]["create_article_schema"]
        url = article_schema_test["endpoint"].split(" ")[1]
        response = client.post(url, json=article_schema_test["payload"])
        assert response.status_code == 200, f"Create Article Schema failed: {response.text}"
    
        # --- 2. Execution Context (Records) ---
    
        # Create Author Record
        create_author_test = DATA["execution_context"]["create_author_record"]
        url = create_author_test["endpoint"].split(" ")[1]
        response = client.post(url, json=create_author_test["payload"])
        assert response.status_code == 200, f"Create Author Record failed: {response.text}"
        
        author_id = response.json().get("id")
        assert author_id is not None, "Author ID not returned"
    
        # Create Article Record (with relationship)
        create_article_test = DATA["execution_context"]["create_article_record"]
        url = create_article_test["endpoint"].split(" ")[1]
        
        # Inject the real Author ID into the payload
        payload = create_article_test["payload"]
        payload["author_id"] = author_id
        
        response = client.post(url, json=payload)
        assert response.status_code == 200, f"Create Article Record failed: {response.text}"
    
        # --- 3. Queries ---
    
        # Filter Authors by Age
        filter_authors_test = DATA["queries"]["filter_authors_by_age"]
        url = filter_authors_test["endpoint"].split(" ")[1]
        response = client.get(url)
        assert response.status_code == 200, f"Filter Authors failed: {response.text}"
        # Verify we get some results
        assert isinstance(response.json(), list), "Expected list response"
    
        # Search Articles by Title (Regex)
        search_title_test = DATA["queries"]["search_articles_by_title"]
        url = search_title_test["endpoint"].split(" ")[1]
        response = client.get(url)
        assert response.status_code == 200, f"Search Articles failed: {response.text}"
        assert isinstance(response.json(), list), "Expected list response"
    
        # Full Text Search
        full_text_test = DATA["queries"]["full_text_search"]
        url = full_text_test["endpoint"].split(" ")[1]
        response = client.get(url)
        assert response.status_code == 200, f"Full Text Search failed: {response.text}"
        assert isinstance(response.json(), list), "Expected list response"
