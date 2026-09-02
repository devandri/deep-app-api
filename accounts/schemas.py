# accounts/schemas.py
from ninja import Schema
from typing import Optional, TypeVar, Generic, Any
from datetime import datetime
from pydantic import Field, BaseModel, field_validator

T = TypeVar('T')

class BaseResponse(Schema, Generic[T]):
    status: str = "success"
    code: str = None
    message: str = ""
    data: Optional[T] = None
    timestamp: str = None
    
    @staticmethod
    def success(data: Any = None, message: str = "Success") -> dict:
        return {
            "status": "success",
            "message": message,
            "data": data,
            "timestamp": datetime.utcnow().isoformat() + "Z"
        }
        
    @staticmethod
    def error(message: str = "Error", code: str = None, data: Any = None) -> dict:
        return {
            "status": "error",
            "message": message,
            "code": code,
            "data": data,
            "timestamp": datetime.utcnow().isoformat() + "Z"
        }

# ============ REQUEST SCHEMAS ============

class DeleteUserRequest(Schema):
    pass

class RestoreUserRequest(Schema):
    pass

class DeleteMultipleRequest(Schema):
    user_ids: list[int]

# ============ USER SCHEMAS ============

class UserCreateSchema(Schema):
    username: str
    email: str
    password: str
    first_name: Optional[str] = ""
    last_name: Optional[str] = ""

class UserUpdateSchema(Schema):
    username: str
    email: str
    first_name: Optional[str] = ""
    last_name: Optional[str] = ""

class UserResponseSchema(Schema):
    id: int
    username: str
    email: str
    first_name: str
    last_name: str
    is_active: bool
    date_joined: Optional[datetime] = None

# ============ AUTH SCHEMAS ============

class LoginSchema(Schema):
    username: str  # Bisa username atau email
    password: str

class RegisterSchema(Schema):
    username: str
    email: str
    password: str
    confirm_password: str
    first_name: Optional[str] = ""
    last_name: Optional[str] = ""

class RefreshTokenSchema(Schema):
    refresh: str

class LogoutSchema(Schema):
    refresh: Optional[str] = None

class TokenResponseSchema(Schema):
    access: str
    refresh: str
    user: Optional[dict] = None

# ============ RESPONSE SCHEMAS ============

class ErrorResponseSchema(Schema):
    error: str
    detail: Optional[str] = None

class SuccessResponseSchema(Schema):
    success: bool
    message: str
    
class UserSoftDeleteResponse(Schema):
    success: bool
    message: str
    user_id: int
    username: str
    deleted_at: Optional[datetime] = None
    
class UserRestoreResponse(Schema):
    success: bool
    message: str
    user_id: int
    username: str
    restored_at: datetime
    
class UserDetailSchema(Schema):
    id: int
    username: str
    email: str
    first_name: str
    last_name: str
    is_active: bool
    id_deleted: bool
    deleted_at: Optional[datetime]
    date_joined: datetime
    
# Pagination Schemas
class PaginationParams(Schema):
    page: int = Field(1, ge=1, description="Page number (starts from 1)")
    per_page: int = Field(10, ge=1, le=100, description="Items per page (max 100)")

class PaginatedResponse(Schema):
    total: int
    page: int
    per_page: int
    total_pages: int
    has_next: bool
    has_previous: bool
    
# Filter Schemas
class UserFilterParams(Schema):
    username: Optional[str] = Field(None, description="Filter by username (contains)")
    email: Optional[str] = Field(None, description="")
    first_name: Optional[str] = Field(None, description="")
    last_name: Optional[str] = Field(None, description="")
    is_active: Optional[bool] = Field(None, description="")
    is_staff: Optional[bool] = Field(None, description="")
    is_superuser: Optional[bool] = Field(None, description="")
    role: Optional[str] = Field(None, description="")
    date_joined_after: Optional[datetime] = Field(None, description="")
    date_joined_before: Optional[datetime] = Field(None, description="")
    search: Optional[str] = Field(None, description="Search in username, email, first_name and last_name")

# Sorting Schemas
class SortParams(Schema):
    sort_by: Optional[str] = Field(
        'date_joined',
        description="Sort field: username, email, first_name, last_name, date_joined, last_login"
    )
    sort_order: Optional[str] = Field(
        'desc',
        description="",
        pattern="^(asc|desc)$"
    )
    
# Combined request params
class UserListRequest(PaginationParams, UserFilterParams, SortParams):
    pass

class ChangePasswordSchema(BaseModel):
    old_password: str = Field(..., description="The user's current password for verification")
    new_password: str = Field(..., min_length=8, description="The new secure password")
    confirm_new_password: str = Field(..., min_length=8, description="Repeat the new secure password")

    # this error format not match with standard error schema (BaseResponse)
    @field_validator("confirm_new_password")
    @classmethod
    def passwords_match(cls, v: str, info):
        if 'new_password' in info.data and v != info.data['new_password']:
            raise ValueError('The two new password fields do not match')
        return v