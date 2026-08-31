# accounts/services.py
from django.contrib.auth import authenticate, get_user_model
from django.db.models import Q
from django.contrib.auth.hashers import make_password
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.exceptions import TokenError
from typing import Optional, List, Dict, Any
from .schemas import UserCreateSchema, UserUpdateSchema
import logging
from django.utils import timezone

logger = logging.getLogger(__name__)
User = get_user_model()

class UserService:
    
    @staticmethod
    def soft_delete_user(user_id: int, deleted_by_id: Optional[int] = None) -> Dict[str, Any]:
        
        try:
            user = User.objects.get(id=user_id)
            
            if user.is_deleted:
                raise ValueError(f"User {user_id} is already deleted")
            
            if user.is_superuser:
                raise PermissionError("Cannot delete superuser")

            username = user.username
            email = user.email
            
            user.delete()
            
            log_message = {
                f"User {username} (ID: {user_id}, Email: {email}) "
                f"soft deleted by user ID: {deleted_by_id or 'system'}"
            }
            logger.info(log_message)

            return {
                'success': True,
                'user_id': user_id,
                'username': username,
                'deleted_at': user.deleted_at,
                'message': f"User {username} soft deleted successfully"
            }
            
        except User.DoesNotExist:
            logger.warning(f"Attempt to delete non-existent user ID: {user_id}")
            raise
        
        except ValueError as e:
            logger.warning(f"Delete failed for user {user_id}: {str(e)}")
            raise
        
        except PermissionError as e:
            logger.warning(f"Permission denied for user {user_id}: {str(e)}")
            raise
        
        except Exception as e:
            logger.error(f"Unexpected error deleting user {user_id}: {str(e)}", exc_info=True)
            raise
        
    @staticmethod
    def restore_user(user_id: int, restored_by_id: Optional[int] = None) -> Dict[str, Any]:
        
        try:
            user = User.all_objects.get(id=user_id)
            
            if not user.is_deleted:
                raise ValueError(f"User {user_id} is not deleted")
            
            user.restore()
            
            logger.info(
                f"User {user.username} (ID: {user_id}) "
                f"restored by user ID: {restored_by_id or 'system'}"
            )
            
            return {
                'success': True,
                'user_id': user_id,
                'username': user.username,
                'restored_at': timezone.now(),
                'message': f"User {user.username} restored successfully"
            }
            
        except User.DoesNotExist:
            logger.warning(f"Attempt to restore non-existent user ID: {user_id}")
            raise
        
        except ValueError as e:
            logger.warning(f"Restore failed for user {user_id}: {str(e)}")
            raise
        
        except Exception as e:
            logger.error(f"Unexpected error restoring user {user_id}: {str(e)}", exc_info=True)
            raise
        
    def hard_delete_user(user_id: int, deleted_by_id: Optional[int] = None) -> Dict[str, Any]:
        
        try:
            user = User.all_objects.get(id=user_id)
            
            username = user.username
            
            user.hard_delete()
            
            logger.warning(
                f"User {username} (ID: {user_id}) "
                f"permanently deleted by user ID: {deleted_by_id or 'system'}"
            )
            
            return {
                'success': True,
                'user_id': user_id,
                'username': username,
                'message': f"User {username} permanently deleted"
            }
            
        except User.DoesNotExist:
            logger.warning(f"Attempt to hard delete non-existent user ID: {user_id}")
            raise
        
        except Exception as e:
            logger.error(f"Unexcpected error hard deleteing user {user_id}: {str(e)}", exc_info=True)
            raise
        
    @staticmethod
    def delete_multiple_users(user_ids: List[int], deleted_by_id: Optional[int] = None) -> Dict[str, Any]:
        
        results = {
            'success': [],
            'failed': [],
            'total': len(user_ids)
        }
        
        for user_id in user_ids:
            try:
                result = UserService.soft_delete_user(user_id, deleted_by_id)
                results['success'].append({
                    'user_id': user_id,
                    'username': result['username']
                })
            except Exception as e:
                results['failed'].append({
                    'user_id': user_id,
                    'error': str(e)
                })
                
        return {
            'success': True,
            'results': results,
            'message': f"Deleted {len(results['success'])} of {len(user_ids)} users"
        }
        
    @staticmethod
    def get_deleted_users() -> List[User]:
        return User.all_objects.filter(deleted_at__isnull=False).order_by('-deleted_at')

    @staticmethod
    def get_user_detail(user_id: int) -> Optional[User]:
        try:
            return User.all_objects.get(id=user_id)
        except User.DoesNotExist:
            return None
        
    @staticmethod
    def is_user_deleted(user_id: int) -> bool:
        try:
            user = User.all_objects.get(id=user_id)
            return user.is_deleted
        except User.DoesNotExist:
            return False
        
# Overwrite existing function "delete_user" before soft deleted
def delete_user(user_id: int) -> None:
    UserService.soft_delete_user(user_id)
        
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