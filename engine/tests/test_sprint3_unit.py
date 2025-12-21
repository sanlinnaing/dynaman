import unittest
from unittest.mock import AsyncMock, MagicMock
from datetime import datetime
from bson import ObjectId

# Import code under test
from execution_context.application.record_use_cases import RecordUseCase
from execution_context.domain.query_parser import parse_filters
from building_blocks.types import FieldType
from metadata_context.domain.entities.schema import SchemaEntity, FieldDefinition

class TestSprint3(unittest.IsolatedAsyncioTestCase):
    async def asyncSetUp(self):
        self.record_repo = AsyncMock()
        self.schema_repo = AsyncMock()
        self.use_case = RecordUseCase(self.record_repo, self.schema_repo)

    def test_query_parser(self):
        params = {"age_gt": 18, "name_contains": "john", "status_eq": "active"}
        result = parse_filters(params)
        expected = {
            "age": {"$gt": 18},
            "name": {"$regex": "john", "$options": "i"},
            "status": {"$eq": "active"}
        }
        self.assertEqual(result, expected)

    def test_query_parser_type_casting(self):
        params = {"age_gt": "18", "is_active_eq": "true", "score_lt": "95.5"}
        type_map = {"age": "number", "is_active": "boolean", "score": "number"}
        result = parse_filters(params, type_map)
        expected = {
            "age": {"$gt": 18},
            "is_active": {"$eq": True},
            "score": {"$lt": 95.5}
        }
        self.assertEqual(result, expected)

    async def test_list_records_with_filters(self):
        entity_name = "User"
        schema_data = {
            "entity_name": entity_name,
            "fields": [
                {"name": "name", "field_type": "string"},
                {"name": "age", "field_type": "number"}
            ]
        }
        self.schema_repo.get_by_name.return_value = schema_data
        
        # Mock repository find return
        mock_records = [{"_id": ObjectId(), "entity": entity_name, "content": {"name": "John", "age": 25}}]
        self.record_repo.find.return_value = mock_records

        filters = {"age_gt": 20}
        await self.use_case.list_records(entity_name, filters)

        # Verify repo.find was called with parsed filters
        expected_filters = {"age": {"$gt": 20}}
        self.record_repo.find.assert_called_with(entity_name, expected_filters, skip=0, limit=50)

    async def test_create_record_with_valid_reference(self):
        entity_name = "Comment"
        valid_oid = str(ObjectId())
        schema_data = {
            "entity_name": entity_name,
            "fields": [
                {"name": "text", "field_type": "string"},
                {"name": "author_id", "field_type": "reference", "reference_target": "User"}
            ]
        }
        self.schema_repo.get_by_name.return_value = schema_data
        self.record_repo.create.return_value = "new_record_id"
        self.record_repo.check_uniqueness.return_value = True

        payload = {"text": "Hello", "author_id": valid_oid}
        result = await self.use_case.create_new_record(entity_name, payload)
        self.assertEqual(result, "new_record_id")

    async def test_create_record_with_invalid_reference(self):
        entity_name = "Comment"
        invalid_oid = "not-an-object-id"
        schema_data = {
            "entity_name": entity_name,
            "fields": [
                {"name": "text", "field_type": "string"},
                {"name": "author_id", "field_type": "reference", "reference_target": "User"}
            ]
        }
        self.schema_repo.get_by_name.return_value = schema_data

        payload = {"text": "Hello", "author_id": invalid_oid}
        
        with self.assertRaises(Exception) as cm:
             await self.use_case.create_new_record(entity_name, payload)
        
        # The exception might be DomainError or ValidationError depending on how it's wrapped
        # In record_use_cases.py, ValidationError is caught and re-raised as DomainError
        self.assertTrue("Validation failed" in str(cm.exception) or "Invalid ObjectId" in str(cm.exception))

if __name__ == "__main__":
    unittest.main()
