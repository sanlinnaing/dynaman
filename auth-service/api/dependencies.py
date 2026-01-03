from motor.motor_asyncio import AsyncIOMotorClient
from config import settings
from infrastructure.user_repository import UserRepository
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jose import jwt, JWTError
from domain.services.security_service import SecurityService # Assuming you might need this or just config
from domain.entities.user import User

db_client = AsyncIOMotorClient(settings.MONGODB_URL)

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/token")

async def get_db():
    return db_client[settings.DATABASE_NAME]

async def get_user_repository(db = Depends(get_db)):
    return UserRepository(db)

async def get_current_user(
    token: str = Depends(oauth2_scheme),
    user_repo: UserRepository = Depends(get_user_repository)
) -> User:
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
        email: str = payload.get("sub")
        if email is None:
            raise credentials_exception
    except JWTError:
        raise credentials_exception
        
    user = await user_repo.get_by_email(email)
    if user is None:
        raise credentials_exception
    return user
