# Copilot Instructions for SouthDrift

## Documentation Standards

- SPEC.md files: Keep technical descriptions concise and high-level. Include short code examples (5-10 lines) only to illustrate patterns. Do NOT include full implementations, complete functions, or extensive code blocks in SPEC files.
- README.md files: Focus on setup, architecture overview, and developer workflows.
- Code should live in actual source files, not documentation.

## Project Architecture

- API Pattern: Frontend calls FastAPI directly via service layer (no BFF middleware) - matches Angular+FastAPI pattern used in production environments.
- Backend: FastAPI (Python 3.11+), async patterns, in-memory repos (will migrate to DB later)
- Data Flow: All dummy/mock data lives in the backend. The frontend fetches via service modules that call FastAPI endpoints.
- Frontend: Next.js App Router, TypeScript, Tailwind, shadcn/ui, SWR for data fetching, Recharts for charts, Framer Motion for animation. Modular dashboard widgets in `frontend/src/components/dashboard/widgets/`.
- Monorepo: Contains `backend/` (FastAPI), `frontend/` (Next.js + shadcn/ui)
- Pattern: Frontend → FastAPI direct (no BFF middleware)

## Rules

- Always include the current date and time in footer, e.g. `2025-12-30 14:46:00`
- API Calls: Always use `API_ENDPOINTS` from `frontend/src/lib/api.ts`. Never hardcode URLs
- API Calls: Use centralized API configuration (`frontend/src/lib/api.ts`) with `API_ENDPOINTS` constants. Never hardcode API URLs in components.
- API Pattern: Direct FastAPI calls (no BFF) - use `API_ENDPOINTS.patients`, `API_ENDPOINTS.patient(id)`, etc.
- Assistant Responses: Always include datetime footer in ISO 8601 format (YYYY-MM-DD HH:MM)
- Be explicit about required vs optional fields in both backend and frontend
- Code examples in docs: Only short snippets (5-10 lines) to illustrate patterns
- Documentation: SPEC.md = high-level only, no full code. README.md = setup and workflows
- Frontend types must match backend models exactly (field names, data types)
- No PII: Never include personal names, company names, or identifiable information in public repo files
- README.md: Setup, workflows, architecture overview only
- SPEC.md: High-level descriptions and decisions only. NO full code implementations
- Types: Frontend types must match backend models exactly. Update both when changing either
- Use enum types (e.g., `DataStatus`) instead of boolean flags for state
- When changing backend models, update frontend types immediately

## UI/UX Rules

- Error Handling: UI components must gracefully handle backend/API downtime (show user-friendly errors, never crash on null/invalid data).
- UI: Use shadcn/ui primitives for all new components. Place dashboard widgets in `frontend/src/components/dashboard/widgets/`.
- Separate UI (presentational) from logic (hooks/services) with orchestrator components
- Type Safety: Shared types in `frontend/types/`. Always align frontend models with backend API responses.

---
For more, see `README.md` in the repo root and `frontend/README.md` for dev setup.
