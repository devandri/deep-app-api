from typing import Optional
from datetime import datetime
from .schemas import BaseResponse

class UserResource:
    @staticmethod
    def format_datetime(dt: Optional[datetime]) -> Optional[str]:
        if not dt:
            return None
        return dt.strftime("%Y-%m-%dT%H:%M:%SZ")

    @staticmethod
    def get_role(user) -> str:
        if user.is_superuser:
            return "superuser"
        if user.is_staff:
            return "admin"
        return "user"
    
    @classmethod
    def make(cls, user) -> dict:
        return {
            "id": user.id,
            "username": user.username,
            "email": user.email,
            "fullname": f"{user.first_name} {user.last_name}".strip(),
            "first_name": user.first_name,
            "last_name": user.last_name,
            "role": cls.get_role(user),
            "is_active": user.is_active,
            "joined_at": cls.format_datetime(user.date_joined),
            "last_login": cls.format_datetime(user.last_login),
        }
        
    @classmethod
    def collection(cls, users) -> list:
        return [cls.make(user) for user in users]
    
class UserDetailResource(UserResource):
    
    @classmethod
    def make(cls, user) -> dict:
        data = super().make(user)
        data.update({
            "is_staff": user.is_staff,
            "is_superuser": user.is_superuser,
            "is_deleted": user.is_deleted if hasattr(user, 'is_deleted') else False,
            "deleted_at": cls.format_datetime(getattr(user, 'deleted_at', None))
        })
        return data