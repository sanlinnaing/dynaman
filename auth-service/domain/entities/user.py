from pydantic import BaseModel, EmailStr, Field, BeforeValidator, ConfigDict
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
    group_ids: list[str] = Field(default_factory=list, description="List of UserGroup IDs this user belongs to")
    provider: str = "local" # local, google, etc.
    
    model_config = ConfigDict(
        populate_by_name=True,
        arbitrary_types_allowed=True,
        json_encoders={ObjectId: str}
    )

class UserCreate(BaseModel):
    email: EmailStr
    password: str
    role: UserRole = UserRole.USER
    group_ids: list[str] = Field(default_factory=list)

class UserUpdate(BaseModel):
    email: Optional[EmailStr] = None
    password: Optional[str] = None
    is_active: Optional[bool] = None
    role: Optional[UserRole] = None
    group_ids: Optional[list[str]] = None