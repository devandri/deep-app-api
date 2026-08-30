# accounts/schemas.py
from ninja import Schema
from typing import Optional
from datetime import datetime

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

# ============ ERROR SCHEMAS ============

class ErrorResponseSchema(Schema):
    error: str
    detail: Optional[str] = None

class SuccessResponseSchema(Schema):
    success: bool
    message: str