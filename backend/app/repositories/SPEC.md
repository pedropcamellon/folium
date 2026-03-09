# Repository Layer Specification

## Overview

Repositories provide data access abstraction for SQLAlchemy models using async PostgreSQL. All repositories follow a consistent interface pattern enforced via Protocol (PEP 544) for static type checking without inheritance constraints.

**Verification:** `mypy app/repositories/` validates all repos match Protocol

**Key Architecture Decisions:**

- **Pattern:** Protocol-based structural typing (no inheritance required)
- **Session Management:** AsyncSession injected per request via FastAPI dependencies
- **Responsibility:** Field name mapping only (camelCase ↔ snake_case) - no type conversion
- **Type Safety:** Pydantic models validate types at API boundary, repositories trust validated data
- **Transactions:** Service layer calls `session.commit()` after repository operations

---

## Repository Interface

All repositories implement these standard CRUD operations:

```python
class RepositoryProtocol(Protocol):
    session: AsyncSession
    
    async def get_all(self) -> list[dict]
    async def get_by_id(self, id: str) -> dict | None
    async def create(self, data: dict) -> dict
    async def update(self, id: str, data: dict) -> dict | None
    async def delete(self, id: str) -> bool
```

Domain-specific methods (e.g., `get_by_patient_id()`) are added as needed.

---

## Implementation Pattern

**Structure:**

```python
class ExampleRepository:
    def __init__(self, session: AsyncSession):
        self.session = session
    
    # CRUD operations using SQLAlchemy queries
    async def get_all(self) -> list[dict]:
        result = await self.session.execute(select(Model))
        return [self._to_dict(m) for m in result.scalars().all()]
    
    # Helper: DB model → API dict (snake_case → camelCase)
    def _to_dict(self, model: Model) -> dict:
        return {"userId": str(model.user_id), ...}
    
    # Helper: API dict → DB fields (camelCase → snake_case)
    def _to_db_fields(self, api_data: dict) -> dict:
        mapping = {"userId": "user_id", ...}
        return {mapping.get(k, k): v for k, v in api_data.items()}
```

**Key Principles:**

- UUID validation and conversion in repository
- Use `.flush()` for operations needing immediate ID, `.commit()` in service layer
- Eager load relationships with `selectinload()` to avoid N+1 queries
- Return `None` for not-found, `False` for failed delete
