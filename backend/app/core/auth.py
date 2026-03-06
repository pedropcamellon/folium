"""Authentication configuration for fastapi-users."""

from typing import Optional
from uuid import UUID

from fastapi import Depends, Request
from fastapi_users import BaseUserManager, FastAPIUsers, UUIDIDMixin
from fastapi_users.authentication import (
    AuthenticationBackend,
    BearerTransport,
    JWTStrategy,
)
from fastapi_users_db_sqlalchemy import SQLAlchemyUserDatabase

from app.config import settings
from app.core.database import get_user_db
from app.models.user import User

# Secret key for JWT (from settings)
SECRET = settings.JWT_SECRET


class UserManager(UUIDIDMixin, BaseUserManager[User, UUID]):
    """Custom user manager for handling user operations."""

    reset_password_token_secret = SECRET
    verification_token_secret = SECRET

    async def on_after_register(self, user: User, request: Optional[Request] = None):
        """Called after successful registration."""
        print(f"User {user.id} has registered with role {user.role}.")

    async def on_after_forgot_password(
        self, user: User, token: str, request: Optional[Request] = None
    ):
        """Called after forgot password request."""
        print(f"User {user.id} has forgotten their password. Reset token: {token}")

    async def on_after_request_verify(
        self, user: User, token: str, request: Optional[Request] = None
    ):
        """Called after verification request."""
        print(f"Verification requested for user {user.id}. Verification token: {token}")


async def get_user_manager(user_db: SQLAlchemyUserDatabase = Depends(get_user_db)):
    """Dependency for getting user manager."""
    yield UserManager(user_db)


def get_jwt_strategy() -> JWTStrategy:
    """Get JWT strategy with configurable expiration."""
    lifetime_seconds = settings.JWT_ACCESS_TOKEN_EXPIRE_MINUTES * 60
    return JWTStrategy(secret=SECRET, lifetime_seconds=lifetime_seconds)


# Bearer transport (JWT in Authorization header)
bearer_transport = BearerTransport(tokenUrl="auth/jwt/login")

# JWT authentication backend
auth_backend = AuthenticationBackend(
    name="jwt",
    transport=bearer_transport,
    get_strategy=get_jwt_strategy,
)

# FastAPIUsers instance
fastapi_users = FastAPIUsers[User, UUID](
    get_user_manager,
    [auth_backend],
)

# Current user dependencies
current_active_user = fastapi_users.current_user(active=True)
current_superuser = fastapi_users.current_user(active=True, superuser=True)
