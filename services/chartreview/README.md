# Chart Review Agent Service

Dedicated Temporal and LangGraph worker for synthetic chart-review draft support.

The backend assembles a validated, traceable patient-context bundle and persists completed reviews. This service runs the bounded agent workflow and returns structured draft-support output. It does not make clinical decisions or recommendations.

## Status

The service directory is reserved for the dedicated worker. The initial LangGraph contracts and mock provider currently live in `backend/` on `feat/chart-review-agent`; move the worker-facing code here when the source-bundle and persistence boundaries are finalized.

## Run

After the service's `pyproject.toml`, worker entry point, and Docker Compose definition are added:

```bash
cd services/chartreview
uv run python -m app.worker
```

For local development, use the mock provider and synthetic input only. The worker will connect to the local Temporal development server configured by the repository Compose stack.

## Responsibilities

- Register the chart-review graph through Temporal's `LangGraphPlugin`.
- Run provider and other I/O nodes as Temporal Activities.
- Validate structured output before returning it to the backend.
- Keep source references traceable to the input bundle.
