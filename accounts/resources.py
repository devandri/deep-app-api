from typing import Optional, List
from datetime import datetime
from .schemas import BaseResponse
import math

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
    
class PaginatedResource:
    @classmethod
    def make(
        cls,
        items: List[dict],
        total: int,
        page: int,
        per_page: int
    ) -> dict:
        total_pages = math.ceil(total/per_page) if per_page > 0 else 0
        
        return {
            "items": items,
            "pagination": {
                "total": total,
                "page": page,
                "per_page": per_page,
                "total_pages": total_pages,
                "has_next": page < total_pages,
                "has_previous": page > 1,
                "from": ((page - 1) * per_page) + 1 if total > 0 else 0,
                "to": min(page * per_page, total) if total > 0 else 0
            }
        }
        
class UserListResource:
    """Specific resource to serving user list with filtering & sorting"""
    @classmethod
    def get_paginated_response(
        cls,
        users,
        page: int,
        per_page: int
    ) -> dict:
        total = users.count()
        start = (page - 1) * per_page
        end = start + per_page
        users_page = users[start:end]
        items = UserResource.collection(users_page)
        
        return PaginatedResource.make(
            items=items,
            total=total,
            page=page,
            per_page=per_page
        )