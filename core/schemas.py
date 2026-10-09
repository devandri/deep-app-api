from typing import Generic, TypeVar
from ninja import Schema
from pydantic import Field

T = TypeVar("T")

class ApiResponse(Schema, Generic[T]):
    success: bool = True
    message: str = "OK"
    data: T | None = None
    
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