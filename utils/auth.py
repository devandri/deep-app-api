from ninja.security import HttpBearer
from rest_framework_simplejwt.tokens import AccessToken
from rest_framework_simplejwt.exceptions import InvalidToken, TokenError
from django.contrib.auth import get_user_model
from django.core.exceptions import ObjectDoesNotExist
import logging

logger = logging.getLogger(__name__)
User = get_user_model()

class AuthBearer(HttpBearer):
    def authenticate(self, request, token: str):
        try:
            access_token = AccessToken(token)
            user_id = access_token.payload.get('user_id')

            if not user_id:
                return None
            
            try:
                user = User.all_objects.get(id=user_id)
            except User.DoesNotExist:
                return None
            
            if user.is_deleted:
                logger.warning(f"Deleted user attempted to access: {user.username} (ID: {user.id})")
                return None
            
            if not user.is_active:
                logger.warning(f"Inactive user attempted to access: {user.username}")
                return None
            
            return user
        
        except (InvalidToken, TokenError) as e:
            logger.warning(f"Invalid token: {str(e)}")
            return None
        except Exception as e:
            logger.error(f"Authentication error: {e}", exc_info=True)
            return None