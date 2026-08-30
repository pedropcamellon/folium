---
applyTo: "**/*.py"
description: "Use when editing Python files in Folium."
---

- Backend: async SQLAlchemy + async PostgreSQL, Alembic migrations, repository pattern, Pydantic validation.
- API Naming Convention: Backend Python uses snake_case for all field names. Pydantic models use `alias` parameter for automatic camelCase conversion at API boundary. Frontend always uses camelCase. Never use camelCase in Python code (repositories, services, database models). Example: `first_name: str = Field(..., alias="firstName")` with `model_config = ConfigDict(populate_by_name=True)`
- Use Pydantic models in FastAPI for request/response validation. Repositories should trust validated data and not perform additional type checks.
- Use Protocols for repository interfaces to allow flexibility in implementation without inheritance constraints.
- Use async SQLAlchemy sessions injected via FastAPI dependencies for all database operations in repositories.
- Use logger from logging instead of print
- Be explicit about required vs optional fields in both backend and frontend
- Use `return` instead of `return None`.
- Use modern Python typing: `str | None`, `list[str]`, and `dict[str, Any]`. Do not use deprecated `typing.Optional`, `typing.List`, or `typing.Dict`.
- Prefer strict contracts: Pydantic models at API, persistence, and external-provider boundaries; frozen `@dataclass` models for validated internal value objects that need no Pydantic behavior. Avoid untyped dicts when a named contract is practical.
- Use enum types (e.g., `DataStatus`) instead of boolean flags for state
- Prefer `pathlib.Path` over string file paths for filesystem operations.