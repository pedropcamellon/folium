# folium frontend

The Next.js frontend provides task-focused clinical workflow and review
surfaces. It calls the backend through centralized API configuration; UI
components do not hardcode API URLs or own workflow policy.

## Run locally

Start the supported local stack from the repository root:

```bash
uv run folium
```

See the [local runtime guide](../docs/dev/local-development.md) for
prerequisites and service controls. Use `pnpm build`, `pnpm lint`, and
`pnpm type-check` for frontend-only production build, lint, and TypeScript
checks.

See the [service boundaries](../docs/dev/architecture/service-boundaries.md)
for the frontend's role in the platform.

See [frontend boundaries](../docs/dev/frontend/overview.md) for the rationale
behind the current client architecture and workflow-state patterns.
