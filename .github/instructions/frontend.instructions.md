---
applyTo: "**/*.{ts,tsx,js,jsx}"
description: "Use when editing TypeScript or JavaScript files in the Folium Next.js frontend."
---

- In Next.js App Router, files are Server Components by default. Any file using React hooks (`useState`, `useEffect`, `useMemo`, etc.) or hook-based UI primitives must include `"use client"` at the top.
- Hooks safety: In Next.js App Router, files are Server Components by default. Any file using React hooks (`useState`, `useEffect`, `useMemo`, etc.) or hook-based UI primitives must include `"use client"` at the top.
- Always ensure `"use client"` is at the top of files using client-side hooks or UI primitives.
- Frontend: TypeScript, Tailwind, shadcn/ui, SWR, Recharts, Framer Motion. Calls FastAPI via service layer; never hardcode API URLs.
- shadcn/ui primitives for new components; dashboard widgets in `frontend/src/components/dashboard/widgets/`.
- Gracefully handle API downtime (no crash on null/invalid). Separate presentational UI from logic. Shared types in `frontend/types/`.