"""Database configuration for user management."""

from typing import AsyncGenerator

from fastapi import Depends
from fastapi_users_db_sqlalchemy import SQLAlchemyUserDatabase
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

from app.models.user import Base

# SQLite database URL (switch to PostgreSQL in Phase 4)
DATABASE_URL = "sqlite+aiosqlite:///../southdrift.db"

# Async engine for SQLite
engine = create_async_engine(DATABASE_URL, echo=False)

# Async session maker
async_session_maker = async_sessionmaker(engine, expire_on_commit=False)


async def create_db_and_tables():
    """Create database tables on startup."""
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)


async def get_async_session() -> AsyncGenerator[AsyncSession, None]:
    """Dependency for getting async database session."""
    async with async_session_maker() as session:
        yield session


async def get_user_db(session: AsyncSession = Depends(get_async_session)):
    """Dependency for getting user database."""
    from app.models.user import User

    yield SQLAlchemyUserDatabase(session, User)
