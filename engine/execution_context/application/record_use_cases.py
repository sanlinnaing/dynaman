from execution_context.infrastructure.record_repository import RecordRepository
from metadata_context.infrastructure.schema_repository import SchemaRepository
from metadata_context.domain.entities.schema import SchemaEntity, FieldDefinition, FieldConstraint
from execution_context.domain.services.validator import build_pydantic_validator
from execution_context.domain.entities.record import RecordMetadata
from execution_context.domain.query_parser import parse_filters
from pydantic import ValidationError
from building_blocks.errors import ValidationErrorDetail, StructuredErrorResponse, DomainError
from datetime import datetime, timezone
from typing import List, Optional

class RecordUseCase:
    """The Orchestrator: Coordinates between Schema Rules and Record Storage"""
    def __init__(self, record_repo: RecordRepository, schema_repo: SchemaRepository):
        self.record_repo = record_repo
        self.schema_repo = schema_repo

    async def create_new_record(self, entity_name: str, payload: dict):
        # 1. Fetch Metadata
        schema_data = await self.schema_repo.get_by_name(entity_name)
        if not schema_data:
            raise DomainError(f"Entity '{entity_name}' not defined.")

        schema = SchemaEntity(**schema_data)
        
        # 2. Advanced validation with dynamic Pydantic model
        validator_model = build_pydantic_validator(schema)
        try:
            validator_model(**payload)
        except ValidationError as e:
            self._handle_validation_error(e, entity_name)

        # Check unique constraints
        await self._check_unique_constraints(schema, entity_name, payload)

        # 3. Create Metadata
        metadata = RecordMetadata(created_at=datetime.now(timezone.utc), updated_at=datetime.now(timezone.utc)).model_dump()

        # 4. Save to Infrastructure
        return await self.record_repo.create(entity_name, payload, metadata)

    async def update_record(self, entity_name: str, record_id: str, payload: dict):
        # 1. Fetch Schema
        schema_data = await self.schema_repo.get_by_name(entity_name)
        if not schema_data:
            raise DomainError(f"Entity '{entity_name}' not defined.")
        
        schema = SchemaEntity(**schema_data)

        # 2. Validate Payload
        validator_model = build_pydantic_validator(schema)
        try:
            validator_model(**payload)
        except ValidationError as e:
            self._handle_validation_error(e, entity_name)

        # Check unique constraints
        await self._check_unique_constraints(schema, entity_name, payload, exclude_record_id=record_id)

        # 3. Prepare Metadata Update
        metadata_update = {"updated_at": datetime.now(timezone.utc)}

        # 4. Update in Infrastructure
        success = await self.record_repo.update(entity_name, record_id, payload, metadata_update)
        if not success:
             raise DomainError(f"Record '{record_id}' not found or update failed.")
        return success

    async def delete_record(self, entity_name: str, record_id: str):
        deleted_at = datetime.now(timezone.utc)
        success = await self.record_repo.soft_delete(entity_name, record_id, deleted_at)
        if not success:
            raise DomainError(f"Record '{record_id}' not found.")
        return success

    async def get_record(self, entity_name: str, record_id: str):
        schema_data = await self.schema_repo.get_by_name(entity_name)
        if not schema_data:
            raise DomainError(f"Entity '{entity_name}' not defined.")
        
        schema = SchemaEntity(**schema_data)
        record = await self.record_repo.get_by_id(entity_name, record_id)
        if not record:
            return None
            
        self._apply_defaults(record, schema)
        return record

    async def list_records(self, entity_name: str, query_params: Optional[dict] = None, skip: int = 0, limit: int = 50):
        """Lists all records for a given entity, applying default values from the schema. Supports filtering."""
        schema_data = await self.schema_repo.get_by_name(entity_name)
        if not schema_data:
            return [] 

        schema = SchemaEntity(**schema_data)
        
        if query_params:
            # Build type map for casting
            field_type_map = {field.name: field.field_type.value for field in schema.fields}
            filters = parse_filters(query_params, field_type_map)
            records = await self.record_repo.find(entity_name, filters, skip=skip, limit=limit)
        else:
            records = await self.record_repo.find_all(entity_name, skip=skip, limit=limit)

        for record in records:
            self._apply_defaults(record, schema)
        
        return records

    async def search_records(self, entity_name: str, query: str, skip: int = 0, limit: int = 50):
        """Full-text search for records of a given entity."""
        schema_data = await self.schema_repo.get_by_name(entity_name)
        if not schema_data:
            return []

        schema = SchemaEntity(**schema_data)
        records = await self.record_repo.search(entity_name, query, skip=skip, limit=limit)
        
        for record in records:
            self._apply_defaults(record, schema)
            
        return records

    async def _check_unique_constraints(self, schema: SchemaEntity, entity_name: str, payload: dict, exclude_record_id: str = None):
        for field in schema.fields:
            if field.constraints and field.constraints.unique:
                value = payload.get(field.name)
                if value is not None:
                    is_unique = await self.record_repo.check_uniqueness(entity_name, field.name, value, exclude_record_id)
                    if not is_unique:
                        error_details = [ValidationErrorDetail(field=field.name, issue="unique_constraint_violation", detail=f"Value '{value}' for field '{field.name}' already exists.")]
                        raise DomainError(f"Validation failed for entity '{entity_name}'", errors=error_details)

    def _apply_defaults(self, record: dict, schema: SchemaEntity):
        if 'content' not in record:
            return
        for field in schema.fields:
            if field.name not in record['content'] and field.default is not None:
                record['content'][field.name] = field.default

    def _handle_validation_error(self, e: ValidationError, entity_name: str):
        error_details: List[ValidationErrorDetail] = []
        for err in e.errors():
            field_name = ".".join(map(str, err['loc']))
            issue_type = err['type'].split('.')[-1]
            if 'pattern' in err['type']:
                issue_type = 'regex_mismatch'
            elif 'email' in err['type']:
                issue_type = 'invalid_email_format'
            elif 'string_too_short' in err['type'] or 'min_length' in err['type']:
                issue_type = 'string_too_short'
            elif 'string_too_long' in err['type'] or 'max_length' in err['type']:
                issue_type = 'string_too_long'
            elif 'less_than_equal' in err['type'] or 'less_than' in err['type']:
                issue_type = 'value_too_high'
            elif 'greater_than_equal' in err['type'] or 'greater_than' in err['type']:
                issue_type = 'value_too_low'
            elif 'literal_error' in err['type']:
                issue_type = 'invalid_enum_value'
            elif 'missing' in err['type']:
                issue_type = 'field_missing'
            elif 'type_error' in err['type']:
                issue_type = 'invalid_type'
            elif 'value_error' in err['type']:
                issue_type = 'value_error'

            error_details.append(
                ValidationErrorDetail(
                    field=field_name,
                    issue=issue_type,
                    detail=err['msg']
                )
            )
        
        structured_response = StructuredErrorResponse(
            message=f"Validation failed for entity '{entity_name}'",
            errors=error_details
        )
        raise DomainError(structured_response.message, errors=error_details)