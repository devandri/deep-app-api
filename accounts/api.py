# accounts/api.py
from ninja import Router, Body
from ninja.security import HttpBearer
from .models import User
from rest_framework_simplejwt.tokens import AccessToken, RefreshToken
from rest_framework_simplejwt.exceptions import TokenError, InvalidToken, ExpiredTokenError

from .schemas import (
    UserCreateSchema, UserUpdateSchema, UserResponseSchema,
    LoginSchema, RegisterSchema, RefreshTokenSchema, LogoutSchema,
    TokenResponseSchema, ErrorResponseSchema, SuccessResponseSchema,
)
from .services import (
    get_users, get_user, create_user, update_user, delete_user,
    authenticate_user, generate_tokens, blacklist_token,
)

# ============ ROUTERS ============

auth_router = Router(tags=["Authentication"])
users_router = Router(tags=["Users"])

# ============ AUTHENTICATION CLASS ============

class AuthBearer(HttpBearer):
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
    response={201: TokenResponseSchema, 400: ErrorResponseSchema},
    auth=None,
    summary="Register new user",
)
def register(request, payload: RegisterSchema):
    """Registrasi user baru"""
    
    if payload.password != payload.confirm_password:
        return 400, {"error": "Passwords do not match"}
    
    if User.objects.filter(username=payload.username).exists():
        return 400, {"error": "Username already exists"}
    
    if User.objects.filter(email=payload.email).exists():
        return 400, {"error": "Email already exists"}
    
    user = User.objects.create_user(
        username=payload.username,
        email=payload.email,
        password=payload.password,
        first_name=payload.first_name or "",
        last_name=payload.last_name or "",
    )
    
    tokens = generate_tokens(user)
    return 201, tokens


@auth_router.post(
    "/login",
    response={200: TokenResponseSchema, 400: ErrorResponseSchema, 401: ErrorResponseSchema},
    auth=None,
    summary="Login with username or email",
)
def login(request, payload: LoginSchema):
    """Login user dengan username atau email"""
    
    username_or_email = payload.username
    password = payload.password
    
    if not username_or_email or not password:
        return 400, {"error": "Username/Email and password are required"}
    
    user = authenticate_user(username_or_email, password)
    
    if not user:
        return 401, {"error": "Invalid credentials"}
    
    tokens = generate_tokens(user)
    return tokens


@auth_router.post(
    "/refresh",
    response={200: TokenResponseSchema, 401: ErrorResponseSchema},
    auth=None,
    summary="Refresh access token",
)
def refresh_token(request, payload: RefreshTokenSchema):
    """Refresh access token menggunakan refresh token"""
    try:
        refresh = RefreshToken(payload.refresh)
        return {
            "access": str(refresh.access_token),
            "refresh": str(refresh),
            "user": None
        }
    except TokenError:
        return 401, {"error": "Invalid refresh token"}


@auth_router.post(
    "/logout",
    response={200: SuccessResponseSchema, 400: ErrorResponseSchema},
    auth=AuthBearer(),
    summary="Logout user",
)
def logout(request, payload: LogoutSchema = Body(None)):
    """Logout dengan men-blacklist refresh token"""
    if payload and payload.refresh:
        success = blacklist_token(payload.refresh)
        if not success:
            return 400, {"error": "Invalid refresh token"}
    
    return {"success": True, "message": "Successfully logged out"}


@auth_router.get(
    "/me",
    response={200: dict, 401: ErrorResponseSchema},
    auth=AuthBearer(),
    summary="Get current user profile",
)
def get_current_user(request):
    """Mendapatkan data user yang sedang login"""
    user = request.auth
    return {
        "id": user.id,
        "username": user.username,
        "email": user.email,
        "first_name": user.first_name,
        "last_name": user.last_name,
        "is_active": user.is_active,
        "is_staff": user.is_staff,
        "is_superuser": user.is_superuser,
        "date_joined": user.date_joined.isoformat() if user.date_joined else None,
        "last_login": user.last_login.isoformat() if user.last_login else None,
    }


# ========================================
# USERS ENDPOINTS (prefix: /api/users/)
# ========================================

@users_router.get(
    "/",
    response={200: list[UserResponseSchema], 401: ErrorResponseSchema},
    auth=AuthBearer(),
    summary="List all users",
)
def list_users(request):
    return get_users()

@users_router.get(
    "/{user_id}",
    response={200: UserResponseSchema, 401: ErrorResponseSchema, 404: ErrorResponseSchema},
    auth=AuthBearer(),
    summary="Get user by ID",
)
def detail(request, user_id: int):
    try:
        return get_user(user_id)
    except User.DoesNotExist:
        return 404, {"error": "User not found"}

@users_router.post(
    "/",
    response={201: UserResponseSchema, 400: ErrorResponseSchema, 401: ErrorResponseSchema},
    auth=AuthBearer(),
    summary="Create new user",
)
def create(request, payload: UserCreateSchema):
    try:
        if User.objects.filter(username=payload.username).exists():
            return 400, {"error": "Username already exists"}
        if User.objects.filter(email=payload.email).exists():
            return 400, {"error": "Email already exists"}
        user = create_user(payload)
        return 201, user
    except Exception as e:
        return 400, {"error": str(e)}

@users_router.put(
    "/{user_id}",
    response={200: UserResponseSchema, 400: ErrorResponseSchema, 401: ErrorResponseSchema, 404: ErrorResponseSchema},
    auth=AuthBearer(),
    summary="Update user",
)
def update(request, user_id: int, payload: UserUpdateSchema):
    try:
        if User.objects.filter(username=payload.username).exclude(id=user_id).exists():
            return 400, {"error": "Username already exists"}
        if User.objects.filter(email=payload.email).exclude(id=user_id).exists():
            return 400, {"error": "Email already exists"}
        user = update_user(user_id, payload)
        return user
    except User.DoesNotExist:
        return 404, {"error": "User not found"}

@users_router.delete(
    "/{user_id}",
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