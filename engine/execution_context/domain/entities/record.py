from pydantic import BaseModel, Field, ConfigDict
from typing import Dict, Any, Optional
from datetime import datetime

class RecordMetadata(BaseModel):
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    deleted_at: Optional[datetime] = None

class RecordEntity(BaseModel):
    """
    Japanese: エンティティ (Entity)
    Represents a single 'row' of user-generated data.
    """
    id: str = Field(default=None, alias="_id")
    entity_name: str
    content: Dict[str, Any]
    version: int = 1
    metadata: RecordMetadata = Field(default_factory=RecordMetadata, alias="_metadata")

    model_config = ConfigDict(populate_by_name=True)