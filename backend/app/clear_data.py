"""Clear interactions and documents from database."""

import asyncio
from sqlalchemy import delete

from app.core.database import async_session_maker
from app.models.db import Interaction, Document


async def main():
    """Clear interactions and documents."""
    async with async_session_maker() as session:
        # Delete documents first (foreign key constraint)
        await session.execute(delete(Document))
        # Then delete interactions
        await session.execute(delete(Interaction))
        await session.commit()
        print("Cleared all interactions and documents")


if __name__ == "__main__":
    asyncio.run(main())
