import unittest
from unittest.mock import AsyncMock
from metadata_context.application.schema_use_cases import SchemaApplicationService
from metadata_context.domain.entities.schema import SchemaEntity, FieldDefinition

class TestSchemaApplicationService(unittest.IsolatedAsyncioTestCase):
    async def asyncSetUp(self):
        self.schema_repo = AsyncMock()
        self.service = SchemaApplicationService(self.schema_repo)
        
        self.sample_schema_data = {
            "entity_name": "TestEntity",
            "fields": [
                {"name": "field1", "field_type": "string"}
            ]
        }
        self.sample_schema = SchemaEntity(**self.sample_schema_data)

    async def test_define_new_entity(self):
        self.schema_repo.save.return_value = None
        result = await self.service.define_new_entity(self.sample_schema_data)
        self.assertEqual(result, "TestEntity")
        self.schema_repo.save.assert_called_once()

    async def test_list_all_entities(self):
        self.schema_repo.list_all.return_value = ["Entity1", "Entity2"]
        result = await self.service.list_all_entities()
        self.assertEqual(result, ["Entity1", "Entity2"])

    async def test_get_entity_definition_found(self):
        self.schema_repo.get_by_name.return_value = self.sample_schema_data
        result = await self.service.get_entity_definition("TestEntity")
        self.assertIsInstance(result, SchemaEntity)
        self.assertEqual(result.entity_name, "TestEntity")

    async def test_get_entity_definition_not_found(self):
        self.schema_repo.get_by_name.return_value = None
        result = await self.service.get_entity_definition("Unknown")
        self.assertIsNone(result)

    async def test_add_field_to_entity_success(self):
        self.schema_repo.get_by_name.return_value = self.sample_schema_data
        field_data = {"name": "new_field", "field_type": "number"}
        
        result = await self.service.add_field_to_entity("TestEntity", field_data)
        
        self.assertIn("added", result)
        self.schema_repo.save.assert_called()
        # Check if version incremented (default 1 -> 2)
        saved_call = self.schema_repo.save.call_args[0][0]
        self.assertEqual(saved_call['version'], 2)
        self.assertEqual(len(saved_call['fields']), 2)

    async def test_add_field_to_entity_not_found(self):
        self.schema_repo.get_by_name.return_value = None
        with self.assertRaises(ValueError):
            await self.service.add_field_to_entity("Unknown", {})

    async def test_remove_field_from_entity_success(self):
        self.schema_repo.get_by_name.return_value = self.sample_schema_data
        result = await self.service.remove_field_from_entity("TestEntity", "field1")
        
        self.assertIn("removed", result)
        saved_call = self.schema_repo.save.call_args[0][0]
        self.assertEqual(len(saved_call['fields']), 0)

    async def test_remove_field_from_entity_not_found(self):
        self.schema_repo.get_by_name.return_value = None
        with self.assertRaises(ValueError):
            await self.service.remove_field_from_entity("Unknown", "field1")

    async def test_update_entity_schema_success(self):
        self.schema_repo.get_by_name.return_value = self.sample_schema_data
        new_data = self.sample_schema_data.copy()
        new_data["fields"] = [] # Clear fields
        
        result = await self.service.update_entity_schema("TestEntity", new_data)
        self.assertIn("updated", result)
        self.schema_repo.save.assert_called()

    async def test_update_entity_schema_mismatch(self):
        self.schema_repo.get_by_name.return_value = self.sample_schema_data
        new_data = {"entity_name": "DifferentName", "fields": []}
        
        with self.assertRaises(ValueError):
            await self.service.update_entity_schema("TestEntity", new_data)

    async def test_update_field_in_entity_success(self):
        self.schema_repo.get_by_name.return_value = self.sample_schema_data
        new_field_data = {"name": "field1", "field_type": "boolean"}
        
        result = await self.service.update_field_in_entity("TestEntity", "field1", new_field_data)
        self.assertIn("updated", result)
        
        saved_call = self.schema_repo.save.call_args[0][0]
        self.assertEqual(saved_call['fields'][0]['field_type'], "boolean")

    async def test_update_field_in_entity_name_mismatch(self):
        self.schema_repo.get_by_name.return_value = self.sample_schema_data
        new_field_data = {"name": "wrong_name", "field_type": "boolean"}
        
        with self.assertRaises(ValueError) as cm:
            await self.service.update_field_in_entity("TestEntity", "field1", new_field_data)
        self.assertIn("must match", str(cm.exception))

    async def test_update_field_in_entity_field_not_found(self):
        self.schema_repo.get_by_name.return_value = self.sample_schema_data
        new_field_data = {"name": "non_existent", "field_type": "boolean"}
        
        with self.assertRaises(ValueError) as cm:
            await self.service.update_field_in_entity("TestEntity", "non_existent", new_field_data)
        self.assertIn("not found in entity", str(cm.exception))

    async def test_delete_entity_schema_success(self):
        self.schema_repo.get_by_name.return_value = self.sample_schema_data
        result = await self.service.delete_entity_schema("TestEntity")
        self.assertIn("deleted", result)
        self.schema_repo.delete.assert_called_with("TestEntity")

    async def test_delete_entity_schema_not_found(self):
        self.schema_repo.get_by_name.return_value = None
        with self.assertRaises(ValueError):
            await self.service.delete_entity_schema("Unknown")

if __name__ == "__main__":
    unittest.main()
