import pytest
from datetime import date, datetime
from metadata_context.domain.entities.schema import SchemaEntity, FieldDefinition, FieldType

def test_validate_payload_success():
    fields = [
        FieldDefinition(name="name", field_type=FieldType.STRING),
        FieldDefinition(name="age", field_type=FieldType.NUMBER),
        FieldDefinition(name="active", field_type=FieldType.BOOLEAN),
        FieldDefinition(name="birthdate", field_type=FieldType.DATE),
    ]
    schema = SchemaEntity(entity_name="Test", fields=fields)
    payload = {"name": "Alice", "age": 30, "active": True, "birthdate": "2000-01-01"}
    schema.validate_payload(payload) # Should not raise

def test_validate_payload_defaults():
    fields = [FieldDefinition(name="role", field_type=FieldType.STRING, default="User")]
    schema = SchemaEntity(entity_name="Test", fields=fields)
    payload = {}
    schema.validate_payload(payload)
    assert payload["role"] == "User"

def test_validate_payload_missing_field():
    fields = [FieldDefinition(name="required", field_type=FieldType.STRING)]
    schema = SchemaEntity(entity_name="Test", fields=fields)
    payload = {}
    with pytest.raises(ValueError, match="Missing field: required"):
        schema.validate_payload(payload)

def test_validate_payload_type_error_number():
    fields = [FieldDefinition(name="age", field_type=FieldType.NUMBER)]
    schema = SchemaEntity(entity_name="Test", fields=fields)
    with pytest.raises(TypeError, match="'age' must be a number"):
        schema.validate_payload({"age": "not a number"})

def test_validate_payload_type_error_string():
    fields = [FieldDefinition(name="name", field_type=FieldType.STRING)]
    schema = SchemaEntity(entity_name="Test", fields=fields)
    with pytest.raises(TypeError, match="'name' must be a string"):
        schema.validate_payload({"name": 123})

def test_validate_payload_type_error_boolean():
    fields = [FieldDefinition(name="active", field_type=FieldType.BOOLEAN)]
    schema = SchemaEntity(entity_name="Test", fields=fields)
    with pytest.raises(TypeError, match="'active' must be a boolean"):
        schema.validate_payload({"active": "yes"})

def test_validate_payload_type_error_date():
    fields = [FieldDefinition(name="bday", field_type=FieldType.DATE)]
    schema = SchemaEntity(entity_name="Test", fields=fields)
    with pytest.raises(TypeError, match="'bday' must be a date string or object"):
        schema.validate_payload({"bday": 123})

def test_add_field_duplicate():
    fields = [FieldDefinition(name="title", field_type=FieldType.STRING)]
    schema = SchemaEntity(entity_name="Test", fields=fields)
    new_field = FieldDefinition(name="title", field_type=FieldType.NUMBER)
    with pytest.raises(ValueError, match="Field 'title' already exists"):
        schema.add_field(new_field)

def test_remove_field_success():
    fields = [FieldDefinition(name="to_remove", field_type=FieldType.STRING)]
    schema = SchemaEntity(entity_name="Test", fields=fields)
    schema.remove_field("to_remove")
    assert len(schema.fields) == 0

def test_remove_field_not_found():
    schema = SchemaEntity(entity_name="Test", fields=[])
    with pytest.raises(ValueError, match="Field 'missing' not found"):
        schema.remove_field("missing")

def test_update_field_success():
    fields = [FieldDefinition(name="old_name", field_type=FieldType.STRING)]
    schema = SchemaEntity(entity_name="Test", fields=fields)
    updated = FieldDefinition(name="new_name", field_type=FieldType.STRING)
    schema.update_field("old_name", updated)
    assert schema.fields[0].name == "new_name"

def test_update_field_rename_collision():
    fields = [
        FieldDefinition(name="f1", field_type=FieldType.STRING),
        FieldDefinition(name="f2", field_type=FieldType.STRING)
    ]
    schema = SchemaEntity(entity_name="Test", fields=fields)
    updated = FieldDefinition(name="f2", field_type=FieldType.STRING)
    with pytest.raises(ValueError, match="Field name 'f2' already exists"):
        schema.update_field("f1", updated)

def test_update_field_not_found():
    schema = SchemaEntity(entity_name="Test", fields=[])
    updated = FieldDefinition(name="any", field_type=FieldType.STRING)
    with pytest.raises(ValueError, match="Field 'missing' not found"):
        schema.update_field("missing", updated)

def test_increment_version():
    schema = SchemaEntity(entity_name="Test", fields=[])
    v1 = schema.version
    schema.increment_version()
    assert schema.version == v1 + 1
