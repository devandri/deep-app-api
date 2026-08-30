# accounts/services.py
from .models import User
from django.contrib.auth import authenticate
from django.db.models import Q
from django.contrib.auth.hashers import make_password
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.exceptions import TokenError
from typing import Optional, List
from .schemas import UserCreateSchema, UserUpdateSchema

# ============ USER SERVICES ============

def get_users() -> List[User]:
    return User.objects.all().order_by('-date_joined')

def get_user(user_id: int) -> User:
    return User.objects.get(id=user_id)

def create_user(data: UserCreateSchema) -> User:
    return User.objects.create(
        username=data.username,
        email=data.email,
        first_name=data.first_name or "",
        last_name=data.last_name or "",
        password=make_password(data.password),
    )

def update_user(user_id: int, data: UserUpdateSchema) -> User:
    user = User.objects.get(id=user_id)
    user.username = data.username
    user.email = data.email
    user.first_name = data.first_name or ""
    user.last_name = data.last_name or ""
    user.save()
    return user

def delete_user(user_id: int) -> None:
    user = User.objects.get(id=user_id)
    user.delete()

# ============ AUTH SERVICES ============

def authenticate_user(username_or_email: str, password: str) -> Optional[User]:
    try:
        user = User.objects.filter(
            Q(username=username_or_email) | Q(email=username_or_email)
        ).first()
        
        if not user:
            return None
        
        return authenticate(username=user.username, password=password)
    except Exception:
        return None

def generate_tokens(user: User) -> dict:
    refresh = RefreshToken.for_user(user)
    return {
        "access": str(refresh.access_token),
        "refresh": str(refresh),
        "user": {
            "id": user.id,
            "username": user.username,
            "email": user.email,
            "first_name": user.first_name,
            "last_name": user.last_name,
        }
    }

def blacklist_token(refresh_token: str) -> bool:
    try:
        token = RefreshToken(refresh_token)
        token.blacklist()
        return True
    except TokenError:
        return False