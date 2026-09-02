# accounts/api.py
from ninja import Router, Body, Query
from ninja.security import HttpBearer
from rest_framework_simplejwt.tokens import AccessToken, RefreshToken
from rest_framework_simplejwt.exceptions import TokenError, InvalidToken, ExpiredTokenError
from .serializers import UserSerializer
import logging
from django.contrib.auth import get_user_model
from .services import UserService
from typing import List
from .auth import AuthBearer
from django.core.exceptions import ValidationError

from .schemas import (
    UserCreateSchema, UserUpdateSchema, UserResponseSchema,
    LoginSchema, RegisterSchema, RefreshTokenSchema, LogoutSchema,
    TokenResponseSchema, ErrorResponseSchema, SuccessResponseSchema,
    UserSoftDeleteResponse, UserRestoreResponse, DeleteMultipleRequest,
    UserDetailSchema, BaseResponse, ChangePasswordSchema,
    PaginationParams, UserFilterParams, SortParams
)
from .services import (
    get_users, get_user, create_user, update_user, delete_user,
    authenticate_user, generate_tokens, blacklist_token,
)
from .resources import UserResource, UserDetailResource, AuthResponseResource
import csv
from django.http import HttpResponse

logger = logging.getLogger(__name__)
User = get_user_model()


# ============ ROUTERS ============

auth_router = Router(tags=["Authentication"])
users_router = Router(tags=["Users"])

# ============ AUTHENTICATION CLASS ============

class _old_AuthBearer(HttpBearer):
    def authenticate(self, request, token: str):
        try:
            access_token = AccessToken(token)
            user_id = access_token.payload.get('user_id')
            user = User.objects.get(id=user_id)
            return user
        except ExpiredTokenError:
            return None
        except (InvalidToken, User.DoesNotExist):
            return None

# ========================================
# AUTH ENDPOINTS (prefix: /api/auth/)
# ========================================

@auth_router.post(
    "/register",
    response={201: BaseResponse, 400: BaseResponse, 409: BaseResponse},
    auth=None,
    summary="Register new user",
)
def register(request, payload: RegisterSchema):
    """Registrasi user baru"""
    
    if payload.password != payload.confirm_password:
        return 400, BaseResponse.error(
            message="Passwords do not match",
            code="password_mismatch"
        )
    
    if User.objects.filter(username=payload.username).exists():
        return 409, BaseResponse.error(
            message="Username already exists",
            code="username_taken"
        )
    
    if User.objects.filter(email=payload.email).exists():
        return 409, BaseResponse.error(
            message="Email already exists",
            code="email_taken"
        )
        
    try:
        user = UserService.register_user(payload)
        refresh = RefreshToken.for_user(user)
        
        return 201, BaseResponse.success(
            data=AuthResponseResource.make(
                user=user,
                access_token=str(refresh.access_token),
                refresh_token=str(refresh)
            ),
            message="User registered successfully"
        )
        
    except ValidationError as e:
        return 400, BaseResponse.error(
            message="Validation error",
            code="validation_error",
            data={
                "errors": e.message_dict
            }
        )
        
    except Exception as e:
        return 400, BaseResponse.error(
            message="Registration failed",
            code="registration_error"
        )
        
    
    # user = User.objects.create_user(
    #     username=payload.username,
    #     email=payload.email,
    #     password=payload.password,
    #     first_name=payload.first_name or "",
    #     last_name=payload.last_name or "",
    # )
    
    # tokens = generate_tokens(user)
    # return 201, tokens


@auth_router.post(
    "/login",
    response={200: BaseResponse, 400: BaseResponse, 401: BaseResponse},
    auth=None,
    summary="Login with username or email",
)
def login(request, payload: LoginSchema):
    """Login user dengan username atau email"""
    
    username_or_email = payload.username
    password = payload.password
    
    if not username_or_email or not password:
        return 400, BaseResponse.error(
            message="Username/Email and password are required",
            code="username_password_required"
        )
    
    user = authenticate_user(username_or_email, password)
    
    if not user:
        return 401, BaseResponse.error(
            message="Invalid credentials",
            code="invalid_credentials"
        )
        
    ## Can not specific error message information, because this is can be security crack  ##
    # if user.is_deleted:
    #     return BaseResponse.error(
    #         message="Account has been deleted",
    #         code="account_deleted"
    #     )
        
    # if not user.is_active:
    #     return BaseResponse.error(
    #         message="Account is inactive",
    #         code="account_inactive"
    #     )
    
    # tokens = generate_tokens(user)
    # return tokens
    access_token, refresh_token = generate_tokens(user)
    
    return BaseResponse.success(
        data=AuthResponseResource.make(
            user=user,
            access_token=access_token,
            refresh_token=refresh_token
        ),
        message="Login successful"
    )


@auth_router.post(
    "/refresh",
    response={200: BaseResponse, 401: BaseResponse},
    auth=None,
    summary="Refresh access token",
)
def refresh_token(request, payload: RefreshTokenSchema):
    """Refresh access token menggunakan refresh token"""
    # try:
    #     refresh = RefreshToken(payload.refresh)
    #     user_id = refresh.payload.get("user_id")
    #     user = User.objects.get(id=user_id)
    #     user_data = UserSerializer(user).data
    #     return {
    #         "access": str(refresh.access_token),
    #         "refresh": str(refresh),
    #         "user": user_data,
    #     }
    # except TokenError:
    #     return 401, {"error": "Invalid refresh token"}
    
    try:
        access_token, refresh_token = generate_tokens(None, payload.refresh)
        return BaseResponse.success(
            data=AuthResponseResource.refresh(access_token, refresh_token),
            message="Token refreshed successfully"
        )
        
    except Exception:
        return BaseResponse.error(
            message="Invalid refresh token",
            code="invalid_refresh_token"
        )


@auth_router.post(
    "/logout",
    response={200: BaseResponse, 400: BaseResponse},
    auth=AuthBearer(),
    summary="Logout user",
)
def logout(request, payload: LogoutSchema = Body(None)):
    """Logout dengan men-blacklist refresh token"""
    try:
        if payload and payload.refresh:
            success = blacklist_token(payload.refresh)
            if not success:
                return 400, BaseResponse.error(
                    message="Invalid refresh token",
                    code="invalid_refresh_token"
                )
        
        return 200, BaseResponse.success(
            message="Successfully logged out"
        )
        
    except:
        return 400, BaseResponse.error(
            message="Logout failed",
            code="logout_failed"
        )

# TODO: GET me
@auth_router.get(
    "/me",
    response={200: BaseResponse, 401: BaseResponse},
    auth=AuthBearer(),
    summary="Get current user profile",
)
def get_current_user(request):
    """Mendapatkan data user yang sedang login"""
    user = request.auth
    return 200, BaseResponse.success(
        data=UserResource.make(user),
        message="Profile retrieved successfully"
    )
    
@auth_router.post(
    "/change-password",
    response={
        200: BaseResponse,
        400: BaseResponse,
        401: BaseResponse,
    },
    auth=AuthBearer(),
    summary="Change password"
)
def change_password(request, payload: ChangePasswordSchema):
    user = request.auth
    
    if not user.check_password(payload.old_password):
        return 400, BaseResponse.error(
            message="Current password is incorrect",
            code="invalid_password"
        )
        
    if payload.old_password == payload.new_password:
        return 400, BaseResponse.error(
            message="New password cannot be the same with old password",
            code="password_cannot_be_the_same"
        )
        
    # if payload.new_password != payload.confirm_new_password:
    #     return 400, BaseResponse.error(
    #         message="Password do not match",
    #         code="password_mismatch"
    #     )
        
    try:
        user.set_password(payload.new_password)
        user.save()

        return 200, BaseResponse.success(
            message="Password changed successfully"
        )
        
    except:
        return 401, BaseResponse.error(
            message="Failed to change password",
            code="password_change_failed"
        )


# ========================================
# USERS ENDPOINTS (prefix: /api/users/)
# ========================================

# TODO: GET users
@users_router.get(
    "/",
    response=BaseResponse,
    auth=AuthBearer(),
    summary="List all users",
)
def list_users(
    request,
    pagination: PaginationParams = Query(...),
    filters: UserFilterParams = Query(...),
    sort: SortParams = Query(...)
):
    # users = get_users()
    # return BaseResponse.success(
    #     data=UserResource.collection(users),
    #     message="User retrieved successfully"
    # )
    
    if not request.auth.is_staff:
        return BaseResponse.error(
            message="Permission denied",
            code="permission_denied"
        )
        
    try:
        filter_dict = filters.dict(exclude_none=True)
        sort_dict = sort.dict()
        pagination_dict = pagination.dict()
        
        result = UserService.get_filtered_users(
            filters=filter_dict,
            sort_by=sort_dict.get('sort_by', 'date_joined'),
            sort_order=sort_dict.get('sort_order', 'desc'),
            page=pagination_dict.get('page', 1),
            per_page=pagination_dict.get('per_page', 10),
            include_deleted=False
        )
        
        return BaseResponse.success(
            data=result,
            message=f"Users retrieved successfully"
        )
        
    except Exception as e:
        logger.error(f"Error listing users: {e}", exc_info=True)
        return BaseResponse.error(
            message="Failed to retrieve users",
            code="server_error"
        )
    

# TODO: GET user_id
@users_router.get(
    "/{user_id}",
    response={200: BaseResponse, 401: ErrorResponseSchema, 404: BaseResponse},
    auth=AuthBearer(),
    summary="Get user by ID",
)
def detail(request, user_id: int):
    try:
        user = get_user(user_id)
        return BaseResponse.success(
            data=UserDetailResource.make(user),
            message="User detail retrieved successfully"
        )
    except User.DoesNotExist:
        return 404, BaseResponse.error(
            message="User not found",
            code="user_not_found"
        )

@users_router.post(
    "/",
    response={201: BaseResponse, 400: BaseResponse, 401: BaseResponse},
    auth=AuthBearer(),
    summary="Create new user",
)
def create(request, payload: UserCreateSchema):
    try:
        if User.objects.filter(username=payload.username).exists():
            return 400, BaseResponse.error(
                message="Username already exists",
                code="username_exist"
            )
        if User.objects.filter(email=payload.email).exists():
            return 400, BaseResponse.error(
                message="Email already exists",
                code="email_exist"
            )
        user = create_user(payload)
        return 201, BaseResponse.success(
            data=UserResource.make(user),
            message="User created successfully"
        )
    except Exception as e:
        return 400, BaseResponse.error(
            message=str(e)
        )

@users_router.put(
    "/{user_id}",
    response={200: BaseResponse, 400: BaseResponse, 401: BaseResponse, 404: BaseResponse},
    auth=AuthBearer(),
    summary="Update user",
)
def update(request, user_id: int, payload: UserUpdateSchema):
    try:
        
        exist_user = User.objects.filter(id=user_id)
        if not exist_user:
            return 404, BaseResponse.error(
                message="User not found",
                code="user_not_found"
            )
            
        if User.objects.filter(username=payload.username).exclude(id=user_id).exists():
            return 400, BaseResponse.error(
                message="Username already exists",
                code="username_exist"
            )
        
        if User.objects.filter(email=payload.email).exclude(id=user_id).exists():
            return 400, BaseResponse.error(
                message="Email already exists",
                code="email_exist"
            )
        
        user = update_user(user_id, payload)
        return 200, BaseResponse.success(
            message="User updated successfully",
            data=UserResource.make(user)
        )
        
    except Exception as e:
        return 400, BaseResponse.error(
            message=str(e)
        )

@users_router.delete(
    "/{user_id}/old",
    response={200: SuccessResponseSchema, 401: ErrorResponseSchema, 404: ErrorResponseSchema},
    auth=AuthBearer(),
    summary="Delete user",
)
def delete(request, user_id: int):
    try:
        delete_user(user_id)
        return {"success": True, "message": f"User {user_id} deleted successfully"}
    except User.DoesNotExist:
        return 404, {"error": "User not found"}
    
@users_router.delete(
    "/{user_id}",
    response={
        200: UserSoftDeleteResponse,
        400: ErrorResponseSchema,
        401: ErrorResponseSchema,
        403: ErrorResponseSchema,
        404: ErrorResponseSchema,
    },
    auth=AuthBearer(),
    summary="Soft delete user",
    description="""
    description
    """
)
def delete_user_endpoint(request, user_id: int):
    """
    Soft delete user
    """
    try:
        if not request.auth.is_staff:
            return 403, {
                "error": "Permission denied",
                "code": "permission_denied",
                "message": "Only admin can delete users"
            }
            
        if request.auth.id == user_id:
            return 400, {
                "error": "Cannot delete yourself",
                "code": "self_delete",
                "message": "You cannot delete your own account"
            }
            
        result = UserService.soft_delete_user(
            user_id=user_id,
            deleted_by_id=request.auth.id
        )
        
        return 200, {
            "success": True,
            "message": result['message'],
            "user_id": result['user_id'],
            "username": result['username'],
            "deleted_at": result['deleted_at']
        }
        
    except User.DoesNotExist:
        return 404, {
            "error": "User not found",
            "code": "user_not_found"
        }
        
    except ValueError as e:
        return 400, {
            "error": str(e),
            "code": "already_deleted"
        }
        
    except ValueError as e:
        return 403, {
            "error": str(e),
            "code": "permission_denied"
        }
        
    except Exception as e:
        logger.error(f"Error deleting user {user_id}: {e}", exc_info=True)
        return 500, {
            "error": "Internal server error",
            "code": "server_error"
        }
        

@users_router.post(
    "/{user_id}/restore",
    response={
        200: UserRestoreResponse,
        400: ErrorResponseSchema,
        401: ErrorResponseSchema,
        403: ErrorResponseSchema,
        404: ErrorResponseSchema,
    },
    auth=AuthBearer(),
    summary="Restore deleted user",
    description="Return soft deleted user"
)
def restore_user_endpoint(request, user_id: int):
    """Restore deleted user"""

    try:
        if not request.auth.is_staff:
            return 403, {
                "error": "Permission denied",
                "code": "permission_denied"
            }
            
        result = UserService.restore_user(
            user_id=user_id,
            restored_by_id=request.auth.id
        ) 
       
        return 200, {
            "success": True,
            "message": result['message'],
            "user_id": result['user_id'],
            "username": result['username'],
            "restored_at": result['restored_at']
        }
        
    except User.DoesNotExist:
        return 404, {
            "error": "User not found",
            "code": "user_not_found"
        }
        
    except ValueError as e:
        return 400, {
            "error": str(e),
            "message": "not_deleted"
        }
        
    except Exception as e:
        logger.error(f"Error restoring user {user_id}: {e}", exc_info=True)
        return 500, {
            "error": "Internal server error",
            "code": "server_error"
        }
        
@users_router.delete(
    "/{user_id}/hard",
    response={
        200: SuccessResponseSchema,
        401: ErrorResponseSchema,
        403: ErrorResponseSchema,
        404: ErrorResponseSchema,
    },
    auth=AuthBearer(),
    summary="Delete user permanently",
    description=""
)
def hard_delete_user_endpoint(request, user_id: int):
    
    try:
        if not request.auth.is_superuser:
            return 403, {
                "error": "Permission denied",
                "code": "permission_denied",
                "message": "Only super admin can hard delete users"
            }
            
        result = UserService.hard_delete_user(
            user_id=user_id,
            deleted_by_id=request.auth.id
        )
        
        return 200, {
            "success": True,
            "message": result['message']
        }
        
    except User.DoesNotExist:
        return 404, {
            "error": "User not found",
            "code": "user_not_found"
        }
        
    except Exception as e:
        logger.error(f"Error hard deleting user {user_id}: {e}", exc_info=True)
        return 500, {
            "error": "Internal server error",
            "code": "server_error"
        }
        
@users_router.post(
    "/delete-multiple/",
    response={
        200: SuccessResponseSchema,
        400: ErrorResponseSchema,
        401: ErrorResponseSchema,
        403: ErrorResponseSchema,
    },
    auth=AuthBearer(),
    summary="Delete multiple users",
    description=""
)
def delete_multiple_users_endpoint(request, payload: DeleteMultipleRequest):
    
    try:
        if not request.auth.is_staff:
            return 403, {
                "error": "Permission denied",
                "message": "permission_denied"
            }
            
        if request.auth.id in payload.user_ids:
            return 400, {
                "error": "Cannot delete yourself",
                "code": "self_delete",
                "message": "You cannot delete your own account"
            }
            
        result = UserService.delete_multiple_users(
            user_ids=payload.user_ids,
            deleted_by_id=request.auth.id
        )
        
        return 200, {
            "success": True,
            "message": result['message'],
            "data": result['results']
        }
        
    except Exception as e:
        logger.error(f"Error deleting multiple users: {e}", exc_info=True)
        return 500, {
            "error": "Internal server error",
            "code": "server_error"
        }
        
@users_router.get(
    "/deleted/",
    response={
        200: BaseResponse,
        401: BaseResponse,
        403: BaseResponse
    },
    auth=AuthBearer(),
    summary="List deleted users",
    description=""
)
def get_deleted_users_endpoint(
    request,
    pagination: PaginationParams = Query(...),
    filters: UserFilterParams = Query(...),
    sort: SortParams = Query(...),
):
    
    try:
        if not request.auth.is_staff:
            return 403, BaseResponse.error(
                message="Permission denied",
                code="permission_denied"
            )
            
        filter_dict = filters.dict(exclude_none=True)
        sort_dict = sort.dict()
        pagination_dict = pagination.dict()

        result = UserService.get_filtered_users(
            filters=filter_dict,
            sort_by=sort_dict.get('sort_by', 'deleted_at'),
            sort_order=sort_dict.get('sort_order', 'desc'),
            page=pagination_dict.get('page', 1),
            per_page=pagination_dict.get('per_page', 10),
            only_deleted=True
        )
        
        return 200, BaseResponse.success(
            data=result,
            message="Deleted users retrieved"
        )
            
        # deleted_users = UserService.get_deleted_users()
        
        # return 200, BaseResponse.success(
        #     data=UserResource.collection(deleted_users),
        #     message="Deleted users retreived"
        # )
        
    except Exception as e:
        logger.error(f"Error fetching deleted users: {e}", exc_info=True)
        return 401, BaseResponse.error(
            message="Failed to retrieve deleted users",
            code="server_error"
        )
        
@users_router.get(
    "/{user_id}/detail",
    response={
        200: BaseResponse,
        401: ErrorResponseSchema,
        403: ErrorResponseSchema,
        404: ErrorResponseSchema,
    },
    auth=AuthBearer(),
    summary="Get user detail including deleted status",
    description=""
)
def get_user_detail_endpoint(request, user_id: int):
    
    try:
        user = UserService.get_user_detail(user_id)
        
        if not user:
            return 404, {
                "error": "User not found",
                "code": "user_not_found"
            }
            
        if not request.auth.is_staff and request.auth.id != user_id:
            return 403, {
                "error": "Permission denied",
                "code": "permission_denied"
            }
            
        return 200, BaseResponse.success(
            data=UserResource.make(user),
            message="Detail user retreived successfully"
        )
        
    except Exception as e:
        logger.error(f"Error getting user detail {user_id}: {e}", exc_info=True)
        return 500, {
            "error": "Internal error server",
            "code": "server_error"
        }
        
@users_router.get(
    "/export/",
    response=BaseResponse,
    auth=AuthBearer(),
    summary="Export all users (no pagination), json or csv format"
)
def export_users(
    request,
    filters: UserFilterParams = Query(...),
    format: str = 'json',
):
    """
    Export all users matching filters (no pagination)
    Useful for CSV export or data analytics
    """
    if not request.auth.is_staff:
        return BaseResponse.error(
            message="Permission denied",
            code="permission_denied"
        )
        
    try:
        filter_dict = filters.dict(exclude_none=True)
        data = UserService.get_export_data(filter_dict)
        
        if format == 'csv':
            
            response = HttpResponse(content_type='text/csv')
            response['Content-Disposition'] = 'attachment; filename="users.csv"'
            
            writer = csv.DictWriter(response, fieldnames=data[0].keys() if data else [])
            writer.writeheader()
            writer.writerows(data)
            return response
        
        return BaseResponse.success(
            data=data,
            message=f"Exported {len(data)} users"
        )
        
    except Exception as e:
        logger.error(f"Error exporting users: {e}", exc_info=True)
        return BaseResponse.error(
            message="Failed to export users",
            code="server_error"
        )