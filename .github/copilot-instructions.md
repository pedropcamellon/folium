# Copilot Instructions for SouthDrift

## Documentation Standards

- **SPEC.md files**: Keep technical descriptions concise and high-level. Include short code examples (5-10 lines) only to illustrate patterns. Do NOT include full implementations, complete functions, or extensive code blocks in SPEC files.
- **README.md files**: Focus on setup, architecture overview, and developer workflows.
- **Code should live in actual source files**, not documentation.

## Project Architecture

- **Monorepo**: Contains `backend/` (FastAPI), `frontend/` (Next.js + shadcn/ui)
- **Frontend**: Next.js App Router, TypeScript, Tailwind, shadcn/ui, SWR for data fetching, Recharts for charts, Framer Motion for animation. Modular dashboard widgets in `frontend/src/components/dashboard/widgets/`.
- **Backend**: FastAPI (Python 3.11+), async patterns, in-memory repositories for MVP. Will migrate to PostgreSQL/Cosmos DB later.
- **API Pattern**: Frontend calls FastAPI directly via service layer (no BFF middleware) - matches Angular+FastAPI pattern used in production environments.
- **Data Flow**: All dummy/mock data lives in the backend. The frontend fetches via service modules that call FastAPI endpoints.

## Developer Workflows

- **Install dependencies**: Frontend: `pnpm install` in `frontend/`, Backend: `pip install -r requirements.txt` in `backend/`
- **Run frontend**: `pnpm dev` (Next.js dev server on port 3000)
- **Run backend**: `uvicorn app.main:app --reload` (FastAPI on port 8000)
- **Docker**: Use `npm run docker:up` and `npm run docker:down` for full stack
- **Deployment**: GitHub Actions deploys frontend to Vercel, backend to Azure Container Apps

## Conventions & Patterns

- **UI**: Use shadcn/ui primitives for all new components. Place dashboard widgets in `frontend/src/components/dashboard/widgets/`.
- **Type Safety**: Shared types in `frontend/types/`. Always align frontend models with backend API responses.
- **API Calls**: Use centralized API configuration (`frontend/src/lib/api.ts`) with `API_ENDPOINTS` constants. Never hardcode API URLs in components.
- **API Pattern**: Direct FastAPI calls (no BFF) - use `API_ENDPOINTS.patients`, `API_ENDPOINTS.patient(id)`, etc.
- **Error Handling**: UI components must gracefully handle backend/API downtime (show user-friendly errors, never crash on null/invalid data).
- **Sidebar**: Sidebar is a separate client component (`Sidebar.tsx`), collapsible, and uses `react-icons` for icons. Keep icon sizes consistent when collapsed.
- **Testing**: No explicit test framework enforced; follow patterns in existing code if adding tests.

- API calling pattern (always use centralized config):

    ```typescript
    import { API_ENDPOINTS, fetcher } from '@/lib/api';
    
    // In React component with SWR
    const { data: patients } = useSWR(API_ENDPOINTS.patients, fetcher);
    
    // Direct fetch call
    const res = await fetch(API_ENDPOINTS.patient(patientId));
    ```

## Integration Points

- **Backend**: FastAPI (Python), see `backend/app/api/v1/endpoints/` for patient/interaction/document endpoints.
- **Frontend-Backend**: Direct API calls using `API_ENDPOINTS` from `frontend/src/lib/api.ts` (no BFF middleware).
- **API Base URL**: Configured via `NEXT_PUBLIC_API_URL` environment variable (dev: `http://localhost:8000`, prod: Azure Container Apps URL).
- **External Services**: AI modules (e.g., AWS Lambda for transcription, Azure for imaging) are referenced in architecture but mocked in code.

## Examples

- **Add a new dashboard widget**: Place in `frontend/src/components/dashboard/widgets/`, use SWR to fetch from FastAPI via service layer, and shadcn/ui for UI.
- **Add a new backend endpoint**: Implement in `backend/app/api/v1/endpoints/`, create service and repository layers, update types in frontend.
- **Update types**: Edit `shared/types/index.ts` and ensure both backend and frontend use the updated model.

---

## Rules

- Always include the current date and time in footer, e.g. `2025-12-30 14:46:00`
- Never include personal names, company names, or identifiable information in public repo files
- SPEC.md: High-level descriptions and decisions only. NO full code implementations
- Code examples in docs: Only short snippets (5-10 lines) to illustrate patterns
- README.md: Setup, workflows, architecture overview only
- Use enum types (e.g., `DataStatus`) instead of boolean flags for state
- Separate UI (presentational) from logic (hooks/services) with orchestrator components
- Always use centralized `API_ENDPOINTS` from `lib/api.ts`. Never hardcode URLs
- All UI components must handle loading, error, and empty states gracefully
- Frontend types must match backend models exactly (field names, data types)
- When changing backend models, update frontend types immediately
- Be explicit about required vs optional fields in both backend and frontend

---
For more, see `README.md` in the repo root and `frontend/README.md` for dev setup.
