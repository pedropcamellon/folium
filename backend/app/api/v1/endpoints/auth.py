"""Authentication routes using fastapi-users."""

from fastapi import APIRouter

from app.core.auth import auth_backend, fastapi_users
from app.models.user import UserCreate, UserRead, UserUpdate

# Create auth router
auth_router = APIRouter()

# JWT authentication endpoints: /auth/jwt/login, /auth/jwt/logout
auth_router.include_router(
    fastapi_users.get_auth_router(auth_backend),
    prefix="/jwt",
)

# Registration endpoint: /auth/register
auth_router.include_router(
    fastapi_users.get_register_router(UserRead, UserCreate),
)

# User management endpoints: /users/me, /users/{id}
users_router = APIRouter()
users_router.include_router(
    fastapi_users.get_users_router(UserRead, UserUpdate),
)
