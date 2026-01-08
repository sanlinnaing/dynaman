from fastapi import APIRouter, Depends, HTTPException, status
from typing import Annotated, List, Optional
from metadata_context.domain.entities.form_layout import FormLayout, FormLayoutCreate, FormLayoutUpdate
from metadata_context.infrastructure.form_layout_repository import FormLayoutRepository
from api.dependencies import get_layout_repository, require_system_admin, verify_token

router = APIRouter()

@router.get("/resolve/{schema_name}", response_model=Optional[FormLayout])
async def resolve_layout(
    schema_name: str,
    repo: Annotated[FormLayoutRepository, Depends(get_layout_repository)],
    user: Annotated[dict, Depends(verify_token)]
):
    layouts = await repo.get_by_schema(schema_name)
    user_groups = set(user["groups"])
    
    # Priority 1: Specific Group Match
    for layout in layouts:
        layout_groups = set(layout.target_group_ids)
        if not user_groups.isdisjoint(layout_groups):
             return layout
             
    # Priority 2: Default Layout
    for layout in layouts:
        if layout.is_default:
            return layout
            
    # Priority 3: None (Frontend should render default vertical list)
    return None

@router.post("/", response_model=FormLayout, status_code=status.HTTP_201_CREATED)
async def create_layout(
    layout_in: FormLayoutCreate,
    repo: Annotated[FormLayoutRepository, Depends(get_layout_repository)],
    _: Annotated[dict, Depends(require_system_admin)]
):
    layout = FormLayout(**layout_in.model_dump())
    return await repo.create(layout)

@router.get("/by-schema/{schema_name}", response_model=List[FormLayout])
async def get_layouts_by_schema(
    schema_name: str,
    repo: Annotated[FormLayoutRepository, Depends(get_layout_repository)],
    user: Annotated[dict, Depends(verify_token)]
):
    # TODO: Filter by user permissions if not admin
    return await repo.get_by_schema(schema_name)

@router.get("/{layout_id}", response_model=FormLayout)
async def get_layout(
    layout_id: str,
    repo: Annotated[FormLayoutRepository, Depends(get_layout_repository)],
    user: Annotated[dict, Depends(verify_token)]
):
    layout = await repo.get_by_id(layout_id)
    if not layout:
        raise HTTPException(status_code=404, detail="Layout not found")
    return layout

@router.put("/{layout_id}", response_model=FormLayout)
async def update_layout(
    layout_id: str,
    layout_in: FormLayoutUpdate,
    repo: Annotated[FormLayoutRepository, Depends(get_layout_repository)],
    _: Annotated[dict, Depends(require_system_admin)]
):
    updated = await repo.update(layout_id, layout_in.model_dump(exclude_unset=True))
    if not updated:
        raise HTTPException(status_code=404, detail="Layout not found")
    return updated

@router.delete("/{layout_id}")
async def delete_layout(
    layout_id: str,
    repo: Annotated[FormLayoutRepository, Depends(get_layout_repository)],
    _: Annotated[dict, Depends(require_system_admin)]
):
    success = await repo.delete(layout_id)
    if not success:
         raise HTTPException(status_code=404, detail="Layout not found")
    return {"message": "Layout deleted successfully"}
