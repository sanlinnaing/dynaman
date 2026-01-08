from pydantic import BaseModel, Field, BeforeValidator, ConfigDict
from typing import Optional, Annotated
from bson import ObjectId

# Helper for Pydantic v2 + BSON
PyObjectId = Annotated[str, BeforeValidator(str)]

class UserGroup(BaseModel):
    id: Optional[PyObjectId] = Field(alias="_id", default=None)
    name: str = Field(..., min_length=1, description="Unique name of the group (e.g., 'Sales')")
    description: Optional[str] = Field(default=None, description="Description of the group's purpose")
    
    model_config = ConfigDict(
        populate_by_name=True,
        arbitrary_types_allowed=True,
        json_encoders={ObjectId: str}
    )

class UserGroupCreate(BaseModel):
    name: str
    description: Optional[str] = None

class UserGroupUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
