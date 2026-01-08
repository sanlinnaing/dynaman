from fastapi import APIRouter, Depends, HTTPException, status
from typing import Annotated
from domain.entities.user import User, UserRole
from domain.entities.user_group import UserGroup, UserGroupCreate, UserGroupUpdate
from infrastructure.user_group_repository import UserGroupRepository
from api.dependencies import get_user_group_repository, get_current_user

router = APIRouter()

def require_system_admin(current_user: User = Depends(get_current_user)):
    if current_user.role != UserRole.SYSTEM_ADMIN:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Requires System Admin privileges"
        )
    return current_user

@router.post("/", response_model=UserGroup, status_code=status.HTTP_201_CREATED)
async def create_group(
    group_in: UserGroupCreate,
    repo: Annotated[UserGroupRepository, Depends(get_user_group_repository)],
    _: Annotated[User, Depends(require_system_admin)]
):
    existing = await repo.get_by_name(group_in.name)
    if existing:
        raise HTTPException(status_code=400, detail="Group with this name already exists")
    
    group = UserGroup(**group_in.model_dump())
    return await repo.create(group)

@router.get("/", response_model=list[UserGroup])
async def list_groups(
    repo: Annotated[UserGroupRepository, Depends(get_user_group_repository)],
    _: Annotated[User, Depends(require_system_admin)]
):
    return await repo.get_all()

@router.get("/{group_id}", response_model=UserGroup)
async def get_group(
    group_id: str,
    repo: Annotated[UserGroupRepository, Depends(get_user_group_repository)],
    _: Annotated[User, Depends(require_system_admin)]
):
    group = await repo.get_by_id(group_id)
    if not group:
        raise HTTPException(status_code=404, detail="Group not found")
    return group

@router.put("/{group_id}", response_model=UserGroup)
async def update_group(
    group_id: str,
    group_in: UserGroupUpdate,
    repo: Annotated[UserGroupRepository, Depends(get_user_group_repository)],
    _: Annotated[User, Depends(require_system_admin)]
):
    updated_group = await repo.update(group_id, group_in.model_dump(exclude_unset=True))
    if not updated_group:
        raise HTTPException(status_code=404, detail="Group not found")
    return updated_group

@router.delete("/{group_id}")
async def delete_group(
    group_id: str,
    repo: Annotated[UserGroupRepository, Depends(get_user_group_repository)],
    _: Annotated[User, Depends(require_system_admin)]
):
    success = await repo.delete(group_id)
    if not success:
         raise HTTPException(status_code=404, detail="Group not found")
    return {"message": "Group deleted successfully"}
