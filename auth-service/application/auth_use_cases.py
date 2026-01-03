from domain.entities.user import User, UserCreate
from domain.services.security_service import SecurityService
from infrastructure.user_repository import UserRepository
from fastapi import HTTPException, status

class AuthUseCases:
    def __init__(self, user_repo: UserRepository):
        self.user_repo = user_repo

    async def register_user(self, user_in: UserCreate):
        existing_user = await self.user_repo.get_by_email(user_in.email)
        if existing_user:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Email already registered"
            )
        
        hashed_password = SecurityService.get_password_hash(user_in.password)
        new_user = User(
            email=user_in.email,
            hashed_password=hashed_password,
            role=user_in.role
        )
        created_user = await self.user_repo.create(new_user)
        return created_user

    async def authenticate_user(self, email: str, password: str):
        user = await self.user_repo.get_by_email(email)
        if not user:
            return None
        if not SecurityService.verify_password(password, user.hashed_password):
            return None
        return user

    async def list_users(self):
        return await self.user_repo.get_all()

    async def delete_user(self, user_id: str):
        return await self.user_repo.delete(user_id)
