from __future__ import annotations
from pydantic import BaseModel, Field, ConfigDict, BeforeValidator
from typing import List, Optional, Any, Dict, Annotated
from datetime import datetime, timezone
from bson import ObjectId

# Helper for Pydantic v2 + BSON
PyObjectId = Annotated[str, BeforeValidator(str)]

class LayoutComponent(BaseModel):
    id: str
    type: str 
    label: Optional[str] = None
    children: List[LayoutComponent] = Field(default_factory=list)
    field_name: Optional[str] = Field(None, alias="fieldName")
    field_type: Optional[str] = Field(None, alias="fieldType")
    structure_type: Optional[str] = Field(None, alias="structureType")
    
    # UI Properties
    required: bool = False
    read_only: bool = Field(False, alias="readOnly")
    placeholder: Optional[str] = None
    helper_text: Optional[str] = Field(None, alias="helperText")
    
    props: Dict[str, Any] = Field(default_factory=dict)

    model_config = ConfigDict(populate_by_name=True)

class FormLayout(BaseModel):
    id: Optional[PyObjectId] = Field(alias="_id", default=None)
    schema_name: str = Field(..., description="The entity_name of the schema this layout applies to")
    name: str
    description: Optional[str] = None
    target_group_ids: List[str] = Field(default_factory=list)
    definition: List[LayoutComponent]
    is_default: bool = False
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

    model_config = ConfigDict(
        populate_by_name=True,
        arbitrary_types_allowed=True,
        json_encoders={ObjectId: str}
    )

class FormLayoutCreate(BaseModel):
    schema_name: str
    name: str
    description: Optional[str] = None
    target_group_ids: List[str] = Field(default_factory=list)
    definition: List[LayoutComponent]
    is_default: bool = False

class FormLayoutUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    target_group_ids: Optional[List[str]] = None
    definition: Optional[List[LayoutComponent]] = None
    is_default: Optional[bool] = None
