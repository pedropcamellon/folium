# Observability

Use correlation IDs, structured logs, workflow state, validation findings, and
evaluation artifacts to make a draft run reviewable.

## Local checks

```bash
docker compose logs -f folium-backend
docker compose logs -f folium-chartreview-worker
docker compose logs -f folium-voicenotes-worker
```

Keep logs free of credentials, tokens, and patient content. Synthetic identifiers
are preferred in examples and fixtures.

## What to record

- Request and workflow correlation identifiers.
- Service and worker state transitions.
- Validation failures and review flags.
- Model, prompt, and dataset versions for evaluation runs.
- Elapsed time and retry outcomes.

The observability stack supports local debugging and audit review. It is not a
production-readiness certification.
