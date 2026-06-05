# Copilot Instructions — Folium

Personal project. Use your personal GitHub account for all git/remote ops, never a work account.

## Architecture

- Monorepo: `backend/` (FastAPI, Python 3.11+), `frontend/` (Next.js App Router + shadcn/ui), AI microservices (voice transcription, medical imaging) orchestrated by backend.
- Backend: async SQLAlchemy + async PostgreSQL, Alembic migrations, repository pattern, Pydantic validation.
- Frontend: TypeScript, Tailwind, shadcn/ui, SWR, Recharts, Framer Motion. Calls FastAPI via service layer; never hardcode API URLs.
- Mock data lives in backend; frontend fetches via service modules.
- Deploy: Docker Compose (local), GitHub Actions (CI/CD), Terraform (IaC), multi-cloud (Azure + AWS).

## Rules

- API Naming Convention: Backend Python uses snake_case for all field names. Pydantic models use `alias` parameter for automatic camelCase conversion at API boundary. Frontend always uses camelCase. Never use camelCase in Python code (repositories, services, database models). Example: `first_name: str = Field(..., alias="firstName")` with `model_config = ConfigDict(populate_by_name=True)`
- API Calls: Use centralized API configuration never hardcode API URLs in components.
- Frontend types must match backend models exactly (field names, data types). When changing backend models, update frontend types immediately
- Types: Frontend types must match backend models exactly. Update both when changing either
- Use Pydantic models in FastAPI for request/response validation. Repositories should trust validated data and not perform additional type checks.
- Use Protocols for repository interfaces to allow flexibility in implementation without inheritance constraints.
- Use async SQLAlchemy sessions injected via FastAPI dependencies for all database operations in repositories.
- Use logger from logging instead of print
- Python: Use `return` instead of `return None`
- Python typing: Use modern union syntax (`str | None`, `list[str]`, `dict[str, Any]`) instead of `Optional`, `List`, `Dict` from typing module
- Be explicit about required vs optional fields in both backend and frontend
- Hooks safety: In Next.js App Router, files are Server Components by default. Any file using React hooks (`useState`, `useEffect`, `useMemo`, etc.) or hook-based UI primitives must include `"use client"` at the top.
- Code examples in docs: Only short snippets (5-10 lines) to illustrate patterns
- No PII: Never include personal names, company names, or identifiable information in public repo files
- Use enum types (e.g., `DataStatus`) instead of boolean flags for state
- No emojis: Never use emojis in code generation (comments, strings, logs, or documentation). Use clear descriptive text instead.
- Assistant Responses: Always include datetime footer in ISO 8601 format (YYYY-MM-DD HH:MM)
- Prefer PS instead bash for CLI commands.

## Input Sanitization

- Repo layer = defense-in-depth: strip whitespace, validate UUIDs, normalize "null"→None, isinstance checks, log Pydantic misses.
- Datetime: pass datetime objects (Pydantic converts); service layer must not `.isoformat()`.
- Max lengths in Pydantic, not repos. ORM params stop SQLi; frontend stops XSS (backend stores raw).

## UI/UX

- shadcn/ui primitives for new components; dashboard widgets in `frontend/src/components/dashboard/widgets/`.
- Gracefully handle API downtime (no crash on null/invalid). Separate presentational UI from logic. Shared types in `frontend/types/`.

## GitHub Workflow

- Prefer `gh` CLI / REST; MCP server only as fallback. Command syntax in the `github-workflow` skill.
- Branches: `feat/<slug>`, `chore/<slug>`, `fix/<slug>`. Rename = create new ref + delete old.
- Issues: shipped work = closed issue (`-r completed`); in-flight = open issue referencing its `feat/*` branch. Mirror each to `tasks/<active|staging|completed>/<issue>-<slug>.md` (`tasks/_TEMPLATE.md`); move between folders as state changes.
- Labels/milestones via `gh` (not MCP); seed set in `tasks/PROJECT-BOARD.md`.
