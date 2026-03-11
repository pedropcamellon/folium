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
        print("[DEBUG seed_db] Calling seed_patients...")
        patients = await seed_patients(session)
        print(f"[DEBUG seed_db] seed_patients returned {len(patients) if patients else 0} patients")
        print(f"[DEBUG seed_db] patients is: {patients}")
        print(f"[DEBUG seed_db] bool(patients) = {bool(patients)}")

        if patients:
            print("[DEBUG seed_db] Patients exist, calling seed_interactions...")
            interactions = await seed_interactions(session, patients)
            print("[DEBUG seed_db] Calling seed_documents...")
            await seed_documents(session, patients, interactions)
        else:
            print("[DEBUG seed_db] No patients found, skipping interactions and documents")

    print("\nDatabase seeding complete!")


if __name__ == "__main__":
    asyncio.run(main())
