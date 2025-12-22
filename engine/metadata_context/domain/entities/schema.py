from pydantic import BaseModel, Field
from typing import List, Any, Optional
from building_blocks.types import FieldType
from datetime import datetime, timezone, date

class FieldConstraint(BaseModel):
    min_value: Optional[float] = None
    max_value: Optional[float] = None
    min_length: Optional[int] = None
    max_length: Optional[int] = None
    enum_list: Optional[List[str]] = None
    regex_pattern: Optional[str] = None
    unique: bool = False

class FieldDefinition(BaseModel):
    name: str
    label: Optional[str] = None
    field_type: FieldType
    default: Any = None
    constraints: Optional[FieldConstraint] = None
    reference_target: Optional[str] = None
    is_required: bool = False

class SchemaEntity(BaseModel):
    """Rich Domain Model: Handles business logic for schemas"""
    entity_name: str
    description: Optional[str] = None
    fields: List[FieldDefinition]
    version: int = 1
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


    def validate_payload(self, payload: dict):
        """Domain Logic: Validates if incoming data matches user-defined types"""
        for field in self.fields:
            if field.name not in payload:
                if field.default is not None:
                    payload[field.name] = field.default
                elif field.is_required:
                    raise ValueError(f"Missing field: {field.name}")
                else:
                    continue
            
            value = payload[field.name]
            if field.field_type == FieldType.NUMBER and not isinstance(value, (int, float)):
                raise TypeError(f"'{field.name}' must be a number")
            if field.field_type == FieldType.STRING and not isinstance(value, str):
                raise TypeError(f"'{field.name}' must be a string")
            if field.field_type == FieldType.BOOLEAN and not isinstance(value, bool):
                raise TypeError(f"'{field.name}' must be a boolean")
            if field.field_type == FieldType.DATE:
                # Basic check, more robust validation could parse string to date
                if not isinstance(value, (str, date, datetime)):
                     raise TypeError(f"'{field.name}' must be a date string or object")

    def add_field(self, new_field: FieldDefinition):
        """Domain Logic: Adds a new field to the schema, ensuring no duplicates."""
        if any(field.name == new_field.name for field in self.fields):
            raise ValueError(f"Field '{new_field.name}' already exists.")
        self.fields.append(new_field)
        self.updated_at = datetime.now(timezone.utc)


    def remove_field(self, field_name: str):
        """Domain Logic: Removes a field from the schema."""
        initial_len = len(self.fields)
        self.fields = [field for field in self.fields if field.name != field_name]
        if len(self.fields) == initial_len:
            raise ValueError(f"Field '{field_name}' not found.")
        self.updated_at = datetime.now(timezone.utc)

    def update_field(self, field_name: str, updated_field: FieldDefinition):
        """Domain Logic: Updates an existing field in the schema."""
        
        # If the name is being changed, ensure the new name doesn't already exist
        if field_name != updated_field.name:
            if any(f.name == updated_field.name for f in self.fields):
                raise ValueError(f"Field name '{updated_field.name}' already exists.")

        field_found = False
        for i, field in enumerate(self.fields):
            if field.name == field_name:
                self.fields[i] = updated_field
                field_found = True
                break
        
        if not field_found:
            raise ValueError(f"Field '{field_name}' not found.")
        
        self.updated_at = datetime.now(timezone.utc)

    def increment_version(self):
        """Domain Logic: Increments the schema version."""
        self.version += 1
        self.updated_at = datetime.now(timezone.utc)