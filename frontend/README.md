# folium frontend

The Next.js frontend provides task-focused clinical workflow and review
surfaces. It calls the backend through centralized API configuration; UI
components do not hardcode API URLs or own workflow policy.

## Local development

Start the supported local stack from the repository root:

```bash
uv run folium
```

See the [local runtime guide](../docs/dev/local-development.md) for
prerequisites and service controls. Use `pnpm build`, `pnpm lint`, and
`pnpm type-check` for frontend-only production build, lint, and TypeScript
checks.

## Azure mock demo deployment

The deployment pipeline targets Azure Static Web Apps Free with preview hybrid
Next.js hosting. CI validates a standalone Next.js build; the SWA deployment
action builds the app from this directory with `NEXT_PUBLIC_API_MODE=mock`.
Hybrid deployment has not yet been verified. The demo uses synthetic,
browser-local fixtures and does not connect to the backend.

See the [deployment guide](../docs/deployment.md) for credentials, the current
demo URL, Terraform, Azure hybrid limitations, and verification status.
