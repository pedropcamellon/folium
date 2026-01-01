"""Base repository interface"""

from abc import ABC, abstractmethod
from typing import List, Optional, TypeVar, Generic
from datetime import datetime
import uuid

T = TypeVar('T')


class BaseRepository(ABC, Generic[T]):
    """Abstract base repository with common CRUD operations"""
    
    def _generate_id(self) -> str:
        """Generate a unique ID"""
        return str(uuid.uuid4())
    
    def _now(self) -> datetime:
        """Get current timestamp"""
        return datetime.utcnow()
    
    @abstractmethod
    async def get_all(self) -> List[T]:
        """Get all records"""
        pass
    
    @abstractmethod
    async def get_by_id(self, id: str) -> Optional[T]:
        """Get record by ID"""
        pass
    
    @abstractmethod
    async def create(self, data: dict) -> T:
        """Create new record"""
        pass
    
    @abstractmethod
    async def update(self, id: str, data: dict) -> Optional[T]:
        """Update existing record"""
        pass
    
    @abstractmethod
    async def delete(self, id: str) -> bool:
        """Delete record"""
        pass
