# Local Docker runtime

Local Docker Compose is the supported development path. The root runtime
command validates Docker and the rendered Compose configuration before starting
services.

```bash
uv run folium
uv run folium status
uv run folium start --rebuild --recreate
uv run folium down
```

The default target is local. Model download is opt-in; a verified GGUF artifact
must be configured before using the download option. Cloud bootstrap commands
are configuration targets and are not required for the local workflow.

## Service checks

Use the runtime status command and Compose logs to check service health. Run
backend maintenance commands through the running backend container so the
configured network and environment are preserved:

```bash
docker compose exec -T folium-backend python -m app.clear_data
docker compose exec -T folium-backend python -m app.seed_db
docker compose exec -T folium-backend pytest tests
```

The reset commands operate on synthetic local data. Do not run them against real
patient data or a production database.
