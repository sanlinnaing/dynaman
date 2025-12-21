from fastapi import APIRouter, Depends, HTTPException
from metadata_context.application.schema_use_cases import SchemaApplicationService
from metadata_context.domain.entities.schema import SchemaEntity, FieldDefinition
from api.dependencies import get_schema_service

router = APIRouter(prefix="/schemas", tags=["Metadata (Builder)"])

@router.get("/")
async def list_schemas(service: SchemaApplicationService = Depends(get_schema_service)):
    """List all available schemas"""
    return await service.list_all_entities()

@router.post("/")
async def create_schema(schema: SchemaEntity, service: SchemaApplicationService = Depends(get_schema_service)):
    """Define a new No-Code Entity"""
    try:
        name = await service.define_new_entity(schema.model_dump())
        return {"message": f"Entity '{name}' created successfully"}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.get("/{name}")
async def get_schema(name: str, service: SchemaApplicationService = Depends(get_schema_service)):
    """Get the definition of an entity"""
    schema = await service.get_entity_definition(name)
    if not schema:
        raise HTTPException(status_code=404, detail="Schema not found")
    return schema

@router.post("/{name}/fields")
async def add_field(name: str, field: FieldDefinition, service: SchemaApplicationService = Depends(get_schema_service)):
    """Add a new field to an entity"""
    try:
        message = await service.add_field_to_entity(name, field.model_dump())
        return {"message": message}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.delete("/{name}/fields/{field_name}")
async def remove_field(name: str, field_name: str, service: SchemaApplicationService = Depends(get_schema_service)):
    """Remove a field from an entity"""
    try:
        message = await service.remove_field_from_entity(name, field_name)
        return {"message": message}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.put("/{name}")
async def update_schema(name: str, schema: SchemaEntity, service: SchemaApplicationService = Depends(get_schema_service)):
    """Update an entire entity definition"""
    try:
        message = await service.update_entity_schema(name, schema.model_dump())
        return {"message": message}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.patch("/{name}")
async def partial_update_schema(name: str, update_data: dict, service: SchemaApplicationService = Depends(get_schema_service)):
    """Partially update an entity definition"""
    try:
        message = await service.partial_update_entity_schema(name, update_data)
        return {"message": message}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.put("/{name}/fields/{field_name}")
async def update_field(name: str, field_name: str, field: FieldDefinition, service: SchemaApplicationService = Depends(get_schema_service)):
    """Update a specific field in an entity"""
    try:
        message = await service.update_field_in_entity(name, field_name, field.model_dump())
        return {"message": message}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.delete("/{name}")
async def delete_schema(name: str, service: SchemaApplicationService = Depends(get_schema_service)):
    """Delete an entire entity definition"""
    try:
        message = await service.delete_entity_schema(name)
        return {"message": message}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))