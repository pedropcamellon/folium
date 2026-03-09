"""Database seeding runner script.

Run with: python -m app.seed_db
"""

import asyncio

from app.core.database import async_session_maker, create_db_and_tables
from app.seed import seed_users, seed_patients, seed_interactions, seed_documents


async def main():
    """Create tables and seed all data."""
    print("Creating database tables...")
    await create_db_and_tables()

    print("\nSeeding database...")

    # Seed users
    async with async_session_maker() as session:
        await seed_users(session)

    # Seed patients, interactions, and documents
    async with async_session_maker() as session:
        patients = await seed_patients(session)

        if patients:
            interactions = await seed_interactions(session, patients)
            await seed_documents(session, patients, interactions)

    print("\n✅ Database seeding complete!")


if __name__ == "__main__":
    asyncio.run(main())
