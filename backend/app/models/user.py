"""User models for authentication and authorization."""

from datetime import datetime, timezone
from enum import Enum
from typing import Optional
from uuid import UUID

from fastapi_users import schemas
from fastapi_users_db_sqlalchemy import SQLAlchemyBaseUserTableUUID
from sqlalchemy import DateTime, String
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column


class Base(DeclarativeBase):
    """Base class for SQLAlchemy models."""

    pass


class UserRole(str, Enum):
    """User roles for role-based access control."""

    ADMIN = "admin"
    PATIENT = "patient"
    PROVIDER = "provider"
    STAFF = "staff"


class User(SQLAlchemyBaseUserTableUUID, Base):
    """User model extending fastapi-users base with custom fields."""

    __tablename__ = "user"

    role: Mapped[str] = mapped_column(String(20), nullable=False, default=UserRole.PATIENT.value)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), nullable=False
    )
    updated_at: Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
        nullable=True,
    )


class UserRead(schemas.BaseUser[UUID]):
    """Schema for reading user data."""

    role: UserRole
    created_at: datetime
    updated_at: datetime


class UserCreate(schemas.BaseUserCreate):
    """Schema for user registration."""

    role: UserRole = UserRole.PATIENT


class UserUpdate(schemas.BaseUserUpdate):
    """Schema for user updates."""

    role: Optional[UserRole] = None
