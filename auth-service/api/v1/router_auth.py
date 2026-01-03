from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from domain.entities.user import User, UserCreate, UserRole
from application.auth_use_cases import AuthUseCases
from infrastructure.user_repository import UserRepository
from api.dependencies import get_user_repository, get_current_user
from domain.services.security_service import SecurityService
from typing import Annotated

router = APIRouter()

@router.post("/users", response_model=User)
async def create_user(
    user_in: UserCreate,
    user_repo: Annotated[UserRepository, Depends(get_user_repository)],
    current_user: Annotated[User, Depends(get_current_user)]
):
    # Authorization Logic
    if current_user.role == UserRole.USER:
         raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to create users"
        )
    
    if current_user.role == UserRole.USER_ADMIN and user_in.role == UserRole.SYSTEM_ADMIN:
         raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="User Admins cannot create System Admins"
        )

    use_cases = AuthUseCases(user_repo)
    return await use_cases.register_user(user_in)

@router.get("/me", response_model=User)
async def read_users_me(current_user: Annotated[User, Depends(get_current_user)]):
    return current_user

@router.get("/users", response_model=list[User])
async def list_users(
    user_repo: Annotated[UserRepository, Depends(get_user_repository)],
    current_user: Annotated[User, Depends(get_current_user)]
):
    if current_user.role == UserRole.USER:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to list users"
        )
    use_cases = AuthUseCases(user_repo)
    return await use_cases.list_users()

@router.delete("/users/{user_id}")
async def delete_user(
    user_id: str,
    user_repo: Annotated[UserRepository, Depends(get_user_repository)],
    current_user: Annotated[User, Depends(get_current_user)]
):
    if current_user.role == UserRole.USER:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to delete users"
        )
    use_cases = AuthUseCases(user_repo)
    
    # Check if target user exists and validate permissions
    target_user = await user_repo.get_by_id(user_id)
    if not target_user:
        raise HTTPException(status_code=404, detail="User not found")
        
    if current_user.role == UserRole.USER_ADMIN and target_user.role == UserRole.SYSTEM_ADMIN:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="User Admins cannot delete System Admins"
        )

    success = await use_cases.delete_user(user_id)
    if not success:
        raise HTTPException(status_code=404, detail="User not found")
    return {"message": "User deleted successfully"}

@router.post("/token")
async def login(
    form_data: Annotated[OAuth2PasswordRequestForm, Depends()],
    user_repo: Annotated[UserRepository, Depends(get_user_repository)]
):
    use_cases = AuthUseCases(user_repo)
    user = await use_cases.authenticate_user(form_data.username, form_data.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token = SecurityService.create_access_token(data={"sub": user.email, "role": user.role})
    return {"access_token": access_token, "token_type": "bearer"}
