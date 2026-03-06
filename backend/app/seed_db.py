"""Database seeding utilities."""

import asyncio
from app.core.database import async_session_maker, create_db_and_tables
from app.models.user import User, UserRole
from passlib.context import CryptContext

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


async def seed_users():
    """Seed initial users for testing."""
    async with async_session_maker() as session:
        # Check if admin already exists
        from sqlalchemy import select

        result = await session.execute(select(User).where(User.email == "admin@southdrift.com"))
        if result.scalar_one_or_none():
            print("Users already seeded")
            return

        # Create test users
        users = [
            User(
                email="admin@southdrift.com",
                hashed_password=pwd_context.hash("Admin123!"),
                role=UserRole.ADMIN.value,
                is_active=True,
                is_superuser=True,
                is_verified=True,
            ),
            User(
                email="provider@southdrift.com",
                hashed_password=pwd_context.hash("Provider123!"),
                role=UserRole.PROVIDER.value,
                is_active=True,
                is_superuser=False,
                is_verified=True,
            ),
            User(
                email="patient@southdrift.com",
                hashed_password=pwd_context.hash("Patient123!"),
                role=UserRole.PATIENT.value,
                is_active=True,
                is_superuser=False,
                is_verified=True,
            ),
        ]

        session.add_all(users)
        await session.commit()
        print("Seeded 3 test users:")
        print("   - admin@southdrift.com / Admin123!")
        print("   - provider@southdrift.com / Provider123!")
        print("   - patient@southdrift.com / Patient123!")


async def main():
    """Create tables and seed users."""
    await create_db_and_tables()
    await seed_users()


if __name__ == "__main__":
    asyncio.run(main())
