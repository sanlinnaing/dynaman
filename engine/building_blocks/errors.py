from pydantic import BaseModel, Field
from typing import List, Optional

class ValidationErrorDetail(BaseModel):
    field: str
    issue: str
    detail: str

class StructuredErrorResponse(BaseModel):
    status: str = "error"
    message: str = Field(..., description="A general message about the error.")
    errors: List[ValidationErrorDetail] = Field(default_factory=list, description="Specific validation errors.")

class DomainError(Exception):
    """Custom exception for domain-level errors."""
    def __init__(self, message: str, errors: Optional[List[ValidationErrorDetail]] = None):
        super().__init__(message)
        self.message = message
        self.errors = errors if errors is not None else []
