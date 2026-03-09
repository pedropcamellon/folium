# Copilot Instructions for SouthDrift

## Documentation Standards

- SPEC.md files: Keep technical descriptions concise and high-level. Include short code examples (5-10 lines) only to illustrate patterns. Do NOT include full implementations, complete functions, or extensive code blocks in SPEC files.
- README.md files: Focus on setup, architecture overview, and developer workflows.
- Code should live in actual source files, not documentation.

## Project Architecture

- API Pattern: Frontend calls FastAPI directly via service layer
- Backend: FastAPI (Python 3.11+), async patterns, SQLAlchemy with async PostgreSQL, Alembic for migrations, repository pattern for data access
- Data Flow: All dummy/mock data lives in the backend. The frontend fetches via service modules that call FastAPI endpoints.
- Frontend: Next.js App Router, TypeScript, Tailwind, shadcn/ui, SWR for data fetching, Recharts for charts, Framer Motion for animation.
- Monorepo: Contains `backend/` (FastAPI), `frontend/` (Next.js + shadcn/ui)
- AI Services: Separate microservices for voice transcription and medical imaging analysis, orchestrated by the backend.
- Deployment: Docker Compose for local dev, GitHub Actions for CI/CD, Terraform for IaC, multi-cloud support (Azure + AWS)

## Rules

- API Calls: Use centralized API configuration never hardcode API URLs in components.
- Be explicit about required vs optional fields in both backend and frontend
- Code examples in docs: Only short snippets (5-10 lines) to illustrate patterns
- No PII: Never include personal names, company names, or identifiable information in public repo files
- Types: Frontend types must match backend models exactly. Update both when changing either
- Use enum types (e.g., `DataStatus`) instead of boolean flags for state
- Frontend types must match backend models exactly (field names, data types). When changing backend models, update frontend types immediately
- Assistant Responses: Always include datetime footer in ISO 8601 format (YYYY-MM-DD HH:MM)

## UI/UX Rules

- Error Handling: UI components must gracefully handle backend/API downtime (show user-friendly errors, never crash on null/invalid data).
- UI: Use shadcn/ui primitives for all new components. Place dashboard widgets in `frontend/src/components/dashboard/widgets/`.
- Separate UI (presentational) from logic (hooks/services) with orchestrator components
- Type Safety: Shared types in `frontend/types/`. Always align frontend models with backend API responses.

---
For more, see `README.md` in the repo root and `frontend/README.md` for dev setup.
