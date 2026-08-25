"""Seed users with all 4 roles."""

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from passlib.context import CryptContext

from app.models.user import User, UserRole

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


async def seed_users(session: AsyncSession) -> None:
    """Seed initial users for testing."""
    # Check if admin already exists
    result = await session.execute(select(User).where(User.email == "admin@folium.com"))
    if result.scalar_one_or_none():
        print("Users already seeded")
        return

    # Create test users with all 4 roles
    users = [
        User(
            email="admin@folium.com",
            hashed_password=pwd_context.hash("Admin123!"),
            role=UserRole.ADMIN.value,
            is_active=True,
            is_superuser=True,
            is_verified=True,
        ),
        User(
            email="provider@folium.com",
            hashed_password=pwd_context.hash("Provider123!"),
            role=UserRole.PROVIDER.value,
            is_active=True,
            is_superuser=False,
            is_verified=True,
        ),
        User(
            email="staff@folium.com",
            hashed_password=pwd_context.hash("Staff123!"),
            role=UserRole.STAFF.value,
            is_active=True,
            is_superuser=False,
            is_verified=True,
        ),
        User(
            email="patient@folium.com",
            hashed_password=pwd_context.hash("Patient123!"),
            role=UserRole.PATIENT.value,
            is_active=True,
            is_superuser=False,
            is_verified=True,
        ),
    ]

    session.add_all(users)
    await session.commit()

    print("Seeded 4 test users:")
    print("   - admin@folium.com / Admin123!")
    print("   - provider@folium.com / Provider123!")
    print("   - staff@folium.com / Staff123!")
    print("   - patient@folium.com / Patient123!")
