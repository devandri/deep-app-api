# accounts/schemas.py
from ninja import Schema
from typing import Optional, TypeVar, Generic, Any
from datetime import datetime

T = TypeVar('T')

class BaseResponse(Schema, Generic[T]):
    status: str = "success"
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
    def error(message: str = "Error", code: str = None) -> dict:
        return {
            "status": "error",
            "message": message,
            "code": code,
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