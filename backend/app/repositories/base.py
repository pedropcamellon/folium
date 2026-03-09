"""Repository protocols and base classes for SQLAlchemy repositories"""

from typing import Protocol
from sqlalchemy.ext.asyncio import AsyncSession


class RepositoryProtocol(Protocol):
    """
    Protocol defining the standard repository interface.

    This uses Python's Protocol (PEP 544) for structural subtyping.
    Any class with these methods is considered compatible - no inheritance needed.
    Type checkers like mypy will verify the interface at static analysis time.
    """

    session: AsyncSession

    async def get_all(self) -> list[dict]:
        """Get all records"""
        ...

    async def get_by_id(self, id: str) -> dict | None:
        """Get record by ID"""
        ...

    async def create(self, data: dict) -> dict:
        """Create new record"""
        ...

    async def update(self, id: str, data: dict) -> dict | None:
        """Update existing record"""
        ...

    async def delete(self, id: str) -> bool:
        """Delete record"""
        ...
