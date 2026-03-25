"""Role-based access control decorators and utilities."""

from collections.abc import Callable
from functools import wraps

from fastapi import Depends, HTTPException, status

from app.core.auth import current_active_user
from app.core.permissions import role_has_permission
from app.models.user import User, UserRole


def require_role(allowed_roles: list[UserRole]) -> Callable:
    """
    Decorator to require specific roles for endpoint access.

    Usage:
        @router.get("/admin-only")
        @require_role([UserRole.ADMIN])
        async def admin_endpoint(user: User = Depends(current_active_user)):
            return {"message": "Admin access granted"}
    """

    def decorator(func: Callable) -> Callable:
        @wraps(func)
        async def wrapper(*args, user: User = Depends(current_active_user), **kwargs):
            user_role = UserRole(user.role)
            if user_role not in allowed_roles:
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail=f"Access denied. Required roles: {[r.value for r in allowed_roles]}",
                )
            return await func(*args, user=user, **kwargs)

        return wrapper

    return decorator


def require_permission(permission: str) -> Callable:
    """Dependency factory that enforces a named permission."""

    async def dependency(user: User = Depends(current_active_user)) -> User:
        user_role = UserRole(user.role)
        if not role_has_permission(user_role, permission):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Missing permission: {permission}",
            )
        return user

    return dependency


async def get_current_provider(user: User = Depends(current_active_user)) -> User:
    """Dependency to ensure current user is a provider."""
    if UserRole(user.role) != UserRole.PROVIDER:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Provider access required",
        )
    return user


async def get_current_admin(user: User = Depends(current_active_user)) -> User:
    """Dependency to ensure current user is an admin."""
    if UserRole(user.role) != UserRole.ADMIN:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin access required",
        )
    return user


async def get_current_patient(user: User = Depends(current_active_user)) -> User:
    """Dependency to ensure current user is a patient."""
    if UserRole(user.role) != UserRole.PATIENT:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Patient access required",
        )
    return user
