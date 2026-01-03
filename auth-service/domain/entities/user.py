from pydantic import BaseModel, EmailStr, Field, BeforeValidator
from typing import Optional, Annotated
from bson import ObjectId
from enum import Enum

# Helper for Pydantic v2 + BSON
PyObjectId = Annotated[str, BeforeValidator(str)]

class UserRole(str, Enum):
    SYSTEM_ADMIN = "system_admin"
    USER_ADMIN = "user_admin"
    USER = "user"

class User(BaseModel):
    id: Optional[PyObjectId] = Field(alias="_id", default=None)
    email: EmailStr
    hashed_password: str
    is_active: bool = True
    role: UserRole = UserRole.USER
    provider: str = "local" # local, google, etc.
    
    class Config:
        populate_by_name = True
        arbitrary_types_allowed = True
        json_encoders = {ObjectId: str}

class UserCreate(BaseModel):
    email: EmailStr
    password: str
    role: UserRole = UserRole.USER
