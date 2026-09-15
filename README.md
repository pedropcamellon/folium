# Folium

Folium is an on-prem-first engineering sandbox for synthetic, reviewable
clinical chart-support workflows. It is not a complete EHR or a generic
clinical-document SaaS product.

[Read the documentation](https://pedropcamellon.github.io/folium/)

## Product boundary

The implemented lane is:

```text
synthetic context -> bounded draft agent -> structured validation
  -> offline evaluation -> MLflow evidence -> Temporal audit -> human review
```

Folium provides draft support only. It does not support real patient data,
diagnosis, treatment recommendations, or autonomous action. Broader retrieval,
confidence calibration, dedicated local serving performance, Azure/AWS providers,
and cloud deployment are planned work, not current capabilities.

## Local runtime

The supported development path uses Docker Compose and the root runtime package.
It validates Docker and rendered Compose configuration before starting services.

```bash
uv run folium
uv run folium status
uv run folium start --rebuild --recreate
uv run folium down
```

The default target is local. Model download is opt-in and requires a verified
GGUF artifact configured in `tools/folium_runtime/src/folium_runtime/model-artifact.toml`.

## Development checks

Run backend maintenance commands through the running backend container so the
configured network and environment are preserved:

```bash
docker compose exec -T folium-backend python -m app.clear_data
docker compose exec -T folium-backend python -m app.seed_db
docker compose exec -T folium-backend pytest tests
```

These reset and seed commands are for synthetic local data only. Do not run them
against real patient data or a production database.

## Repository shape

- `backend/`: FastAPI API, typed contracts, persistence, and workflow orchestration
- `frontend/`: Next.js application and user-facing review surfaces
- `packages/folium-core/`: stable shared contracts and pure primitives
- `services/`: focused transcription, voice-note, summarization, and chart-review services
- `tools/folium_runtime/`: local runtime command
- `docs/`: published user and developer documentation

Start with the [developer guide](https://pedropcamellon.github.io/folium/dev/)
for local operations and extension boundaries. Start with the [user guide](https://pedropcamellon.github.io/folium/user-guide/)
for supported synthetic workflows.
