from typing import Generic, TypeVar
from ninja import Schema

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