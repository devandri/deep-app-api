"""
URL configuration for config project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
# config/urls.py
from django.contrib import admin
from django.urls import path
from ninja import NinjaAPI
from accounts.api import auth_router, users_router

# ============ NINJA API SETUP ============

api = NinjaAPI(
    title="DeepApp API",
    version="1.0.0",
    description="""
    # DeepApp API Documentation
    
    ## 🔐 Authentication
    API ini menggunakan JWT (JSON Web Token) untuk autentikasi.
    
    ### Cara Mendapatkan Token:
    1. **Registrasi**: `POST /api/auth/register`
    2. **Login**: `POST /api/auth/login`
    3. **Gunakan Token**: `Authorization: Bearer <access_token>`
    
    ## 📚 Endpoint Groups
    - **Authentication** (`/api/auth/*`) - Login, Register, Refresh, Logout
    - **Users** (`/api/users/*`) - CRUD Users (🔒 Protected)
    """,
    docs_url="/docs",          # Swagger UI
    openapi_url="/openapi.json", # OpenAPI Schema
)

# Register routers
api.add_router("/auth/", auth_router)   # /api/auth/*
api.add_router("/users/", users_router) # /api/users/*

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/', api.urls),  # Base API: /api/
]