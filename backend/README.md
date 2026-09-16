# folium backend

The FastAPI backend owns clinical data access, validation, and workflow
initiation. It uses PostgreSQL with SQLAlchemy and Alembic, and coordinates
long-running work through Temporal. API documentation is available from the
running service at `/docs`.

The backend uses repositories to separate data access from workflow policy and
a storage-provider boundary to keep local object storage portable. See the
[backend layers](../docs/dev/backend/layers.md),
[repository layer](../docs/dev/backend/repository-layer.md), and
[storage providers](../docs/dev/backend/storage.md) for the rationale. See
[security boundaries](../docs/dev/backend/security.md) for authorization,
validation, and deployment responsibility.

## Local operations

Start the full local runtime from the repository root:

```bash
uv run folium
```

See the [local runtime guide](../docs/dev/local-development.md) for
prerequisites and service controls.

Run maintenance commands through the running backend container:

```bash
docker compose exec -T folium-backend python -m app.seed_db
docker compose exec -T folium-backend pytest tests
```

The local runtime and its data-reset commands are for synthetic development
data only. See the [service boundaries](../docs/dev/architecture/service-boundaries.md)
for the backend's role in the platform.
