from typing import Generic, TypeVar, List, Optional
from ninja import Schema
from pydantic import Field
from datetime import datetime

T = TypeVar("T")

# class ApiResponse(Schema, Generic[T]):
#     success: bool = True
#     message: str = "OK"
#     data: T | None = None

class ApiResponse(Schema, Generic[T]):
    """Standard success envelope."""
    success: bool = True
    status: str = "success"
    code: Optional[int] = None
    message: str = "OK"
    data: Optional[T] = None
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    
class ErrorDetail(Schema):
    field: str | None = None
    message: str
    
class ErrorResponse(Schema):
    success: bool = False
    message: str
    code: str
    errors: list[ErrorDetail] = []
    
class PaginationParams(Schema):
    page: int = Field(1, ge=1, description="Page number (starts from 1)")
    per_page: int = Field(10, ge=1, le=100, description="Items per page (max 100)")
    
class PaginationMeta(Schema):
    total: int
    page: int
    per_page: int
    total_pages: int
    has_next: bool
    has_previous: bool
    start: int = Field(1, alias="from", serialization_alias="from", validation_alias="from")
    end: int = Field(0, alias="to", serialization_alias="to", validation_alias="from")
    
    class Config:
        populate_by_name = True
        
class ListData(Schema, Generic[T]):
    """Nested payload for list endpoints."""
    items: List[T]
    # pagination: PaginationMeta
    pagination: dict