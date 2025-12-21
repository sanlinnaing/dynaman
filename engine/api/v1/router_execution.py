from fastapi import APIRouter, Depends, HTTPException, Request
from fastapi.responses import JSONResponse
from execution_context.application.record_use_cases import RecordUseCase
from api.dependencies import get_record_use_case
from building_blocks.errors import DomainError # New import
from building_blocks.errors import StructuredErrorResponse, ValidationErrorDetail # Also need to import these to properly construct the response detail

router = APIRouter(prefix="/data", tags=["Execution (Runtime)"])

@router.post("/{entity_name}")
async def add_data(
    entity_name: str, 
    payload: dict, 
    service: RecordUseCase = Depends(get_record_use_case)
):
    """Add a record to a specific No-Code entity"""
    try:
        record_id = await service.create_new_record(entity_name, payload)
        return {"id": record_id, "status": "success"}
    except DomainError as e:
        # Construct the detailed error response from the DomainError
        error_response = StructuredErrorResponse(
            message=e.message,
            errors=e.errors
        )
        return JSONResponse(status_code=400, content=error_response.model_dump())
    except Exception as e:
        # Catch any other unexpected errors
        raise HTTPException(status_code=500, detail=f"An unexpected error occurred: {str(e)}")


@router.get("/{entity_name}")
async def list_data(
    entity_name: str,
    request: Request,
    skip: int = 0,
    limit: int = 50,
    service: RecordUseCase = Depends(get_record_use_case)
):
    """Get all records of a specific No-Code entity"""
    try:
        query_params = dict(request.query_params)
        # Remove skip/limit from filters
        if "skip" in query_params: del query_params["skip"]
        if "limit" in query_params: del query_params["limit"]

        records = await service.list_records(entity_name, query_params, skip=skip, limit=limit)
        return records
    except Exception as e:
        raise HTTPException(status_code=404, detail=str(e))

@router.get("/{entity_name}/search")
async def search_data(
    entity_name: str,
    q: str,
    skip: int = 0,
    limit: int = 50,
    service: RecordUseCase = Depends(get_record_use_case)
):
    """Full-text search for records"""
    try:
        records = await service.search_records(entity_name, q, skip=skip, limit=limit)
        return records
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.get("/{entity_name}/{record_id}")
async def get_record(
    entity_name: str, 
    record_id: str, 
    service: RecordUseCase = Depends(get_record_use_case)
):
    """Get a single record by ID"""
    try:
        record = await service.get_record(entity_name, record_id)
        if not record:
            raise HTTPException(status_code=404, detail="Record not found")
        return record
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.put("/{entity_name}/{record_id}")
async def update_record(
    entity_name: str, 
    record_id: str, 
    payload: dict, 
    service: RecordUseCase = Depends(get_record_use_case)
):
    """Update a record"""
    try:
        success = await service.update_record(entity_name, record_id, payload)
        return {"id": record_id, "status": "updated", "success": success}
    except DomainError as e:
        error_response = StructuredErrorResponse(
            message=e.message,
            errors=e.errors
        )
        return JSONResponse(status_code=400, content=error_response.model_dump())
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.delete("/{entity_name}/{record_id}")
async def delete_record(
    entity_name: str, 
    record_id: str, 
    service: RecordUseCase = Depends(get_record_use_case)
):
    """Soft delete a record"""
    try:
        success = await service.delete_record(entity_name, record_id)
        return {"id": record_id, "status": "deleted", "success": success}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))