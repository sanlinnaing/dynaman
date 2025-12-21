from metadata_context.infrastructure.schema_repository import SchemaRepository
from metadata_context.domain.entities.schema import SchemaEntity, FieldDefinition

class SchemaApplicationService:
    """
    Japanese: ユースケース (Use Case)
    Coordinates the process of defining new entities in the no-code tool.
    """
    def __init__(self, schema_repo: SchemaRepository):
        self.schema_repo = schema_repo

    async def define_new_entity(self, schema_data: dict):
        # 1. Create the Domain Entity
        new_schema = SchemaEntity(**schema_data)
        
        # 2. Persist the metadata
        await self.schema_repo.save(new_schema.model_dump())
        return new_schema.entity_name

    async def list_all_entities(self):
        return await self.schema_repo.list_all()

    async def get_entity_definition(self, entity_name: str) -> SchemaEntity:
        data = await self.schema_repo.get_by_name(entity_name)
        if not data:
            return None
        return SchemaEntity(**data)

    async def add_field_to_entity(self, entity_name: str, field_data: dict):
        schema = await self.get_entity_definition(entity_name)
        if not schema:
            raise ValueError(f"Entity '{entity_name}' not found.")
        
        new_field = FieldDefinition(**field_data)
        schema.add_field(new_field)
        schema.increment_version()
        await self.schema_repo.save(schema.model_dump())
        return f"Field '{field_data['name']}' added to entity '{entity_name}'."

    async def remove_field_from_entity(self, entity_name: str, field_name: str):
        schema = await self.get_entity_definition(entity_name)
        if not schema:
            raise ValueError(f"Entity '{entity_name}' not found.")
            
        schema.remove_field(field_name)
        schema.increment_version()
        await self.schema_repo.save(schema.model_dump())
        return f"Field '{field_name}' removed from entity '{entity_name}'."

    async def update_entity_schema(self, name: str, new_schema_data: dict):
        existing_schema = await self.get_entity_definition(name)
        if not existing_schema:
            raise ValueError(f"Entity '{name}' not found.")
        
        if new_schema_data.get("entity_name") != name:
            raise ValueError("Entity name in payload must match entity name in path.")
        
        # Validate the new schema data against the SchemaEntity model
        updated_schema = SchemaEntity(**new_schema_data)
        updated_schema.version = existing_schema.version
        updated_schema.increment_version()
        
        await self.schema_repo.save(updated_schema.model_dump())
        return f"Entity '{name}' schema updated successfully."

    async def update_field_in_entity(self, entity_name: str, field_name: str, new_field_data: dict):
        schema = await self.get_entity_definition(entity_name)
        if not schema:
            raise ValueError(f"Entity '{entity_name}' not found.")

        field_found = False
        for i, field in enumerate(schema.fields):
            if field.name == field_name:
                # Validate new_field_data against FieldDefinition
                updated_field = FieldDefinition(**new_field_data)
                
                # Ensure the name in new_field_data matches field_name
                if updated_field.name != field_name:
                    raise ValueError(f"Field name in payload ('{updated_field.name}') must match field name in path ('{field_name}').")

                schema.fields[i] = updated_field
                field_found = True
                break
        
        if not field_found:
            raise ValueError(f"Field '{field_name}' not found in entity '{entity_name}'.")

        schema.increment_version()
        await self.schema_repo.save(schema.model_dump())
        return f"Field '{field_name}' in entity '{entity_name}' updated successfully."

    async def partial_update_entity_schema(self, entity_name: str, update_data: dict):
        existing_schema = await self.get_entity_definition(entity_name)
        if not existing_schema:
            raise ValueError(f"Entity '{entity_name}' not found.")

        if "entity_name" in update_data and update_data["entity_name"] != entity_name:
            raise ValueError("Entity name in payload cannot be changed.")

        # Prevent changing fields directly, should use field-specific endpoints
        if "fields" in update_data:
            raise ValueError("Fields cannot be updated via this endpoint. Use the field-specific endpoints.")

        # Create a copy of the existing schema and apply the updates
        updated_schema_data = existing_schema.model_dump()
        updated_schema_data.update(update_data)
        
        # Validate the updated data
        updated_schema = SchemaEntity(**updated_schema_data)
        updated_schema.increment_version()

        await self.schema_repo.save(updated_schema.model_dump())
        return f"Entity '{entity_name}' schema updated successfully."

    async def delete_entity_schema(self, entity_name: str):
        existing_schema = await self.get_entity_definition(entity_name)
        if not existing_schema:
            raise ValueError(f"Entity '{entity_name}' not found.")
            
        await self.schema_repo.delete(entity_name)
        return f"Entity '{entity_name}' deleted successfully."