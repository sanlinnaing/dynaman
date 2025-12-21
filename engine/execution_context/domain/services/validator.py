from pydantic import BaseModel, Field, create_model, EmailStr
from pydantic.functional_validators import AfterValidator
from typing import List, Type, Any, Dict, Literal, Annotated, Optional # Added Optional
from bson import ObjectId
from datetime import date # Import date

from building_blocks.types import FieldType
from metadata_context.domain.entities.schema import SchemaEntity, FieldDefinition, FieldConstraint
from execution_context.domain.entities.record import RecordMetadata

def validate_object_id(v: str) -> str:
    if not ObjectId.is_valid(v):
        raise ValueError('Invalid ObjectId')
    return v

ObjectIdStr = Annotated[str, AfterValidator(validate_object_id)]

def build_pydantic_validator(schema_entity: SchemaEntity) -> Type[BaseModel]:
    fields: Dict[str, Any] = {}
    for field_def in schema_entity.fields:
        pydantic_type = _map_field_type_to_pydantic_type(field_def.field_type)
        field_args = _apply_constraints_to_field(field_def.constraints, pydantic_type)

        # Handle enum_list by dynamically creating a Literal type
        if field_def.constraints and field_def.constraints.enum_list:
            pydantic_type = Literal[*field_def.constraints.enum_list] # Create Literal type
            # Remove enum_list from field_args as it's handled by the type itself
            if "enum_list" in field_args:
                del field_args["enum_list"]

        # Apply constraints using Annotated if field_args are present
        if field_args:
            # If default is provided, it should be the second argument in the tuple
            # If no default, the field is required
            if field_def.default is not None:
                fields[field_def.name] = (Annotated[pydantic_type, Field(**field_args)], field_def.default)
            else:
                fields[field_def.name] = (Annotated[pydantic_type, Field(**field_args)], ...)
        elif field_def.default is not None:
            fields[field_def.name] = (pydantic_type, field_def.default)
        else:
            fields[field_def.name] = (pydantic_type, ...) # Required field, no default
            
    # Add _metadata field
    fields["metadata"] = (Optional[RecordMetadata], Field(default=None, alias="_metadata"))

    # Dynamically create the Pydantic model
    DynamicValidator = create_model(schema_entity.entity_name + 'Validator', **fields)
    return DynamicValidator

def _map_field_type_to_pydantic_type(field_type: FieldType) -> Type:
    if field_type == FieldType.STRING:
        return str
    elif field_type == FieldType.NUMBER:
        return float  # Using float to cover both int and float
    elif field_type == FieldType.EMAIL:
        return EmailStr
    elif field_type == FieldType.BOOLEAN:
        return bool
    elif field_type == FieldType.DATE:
        return date
    elif field_type == FieldType.REFERENCE:
        return ObjectIdStr
    # Add other mappings as needed
    return Any  # Fallback for unsupported types

def _apply_constraints_to_field(constraints: FieldConstraint | None, pydantic_type: Type) -> Dict[str, Any]:
    field_kwargs = {}
    if constraints:
        if constraints.min_value is not None:
            field_kwargs["ge"] = constraints.min_value
        if constraints.max_value is not None:
            field_kwargs["le"] = constraints.max_value
        if constraints.min_length is not None:
            field_kwargs["min_length"] = constraints.min_length
        if constraints.max_length is not None:
            field_kwargs["max_length"] = constraints.max_length
        if constraints.regex_pattern is not None:
            field_kwargs["pattern"] = constraints.regex_pattern
    return field_kwargs