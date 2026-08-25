# Temporal Infrastructure

Shared Temporal server infrastructure for local development and testing.

## Quick Start

```powershell
# Start shared PostgreSQL first
cd ../..
docker compose -f docker-compose.database.yml up -d

# Start Temporal infrastructure
cd services/temporal
docker compose up

# Access Temporal UI
Start http://localhost:8233
```

## Architecture

This folder contains the shared Temporal infrastructure used by all Temporal-based services:

- **Temporal PostgreSQL**: Dedicated database for Temporal state (port 5433)
- **Temporal Server**: Workflow orchestration engine (port 7233)
- **Temporal UI**: Web interface for monitoring workflows (port 8233)
- **Prometheus Metrics**: Temporal server metrics endpoint (port 9090)

Temporal uses a dedicated PostgreSQL database (`folium-temporal-postgres`) separate from the application database.

## Usage Patterns

### Starting Temporal Infrastructure

```bash
# From project root
docker compose up temporal temporal-ui -d

# Or rebuild if config changed
docker compose up temporal temporal-ui --build -d
```

### Checking Temporal Health

```bash
# View temporal logs
docker compose logs temporal --tail=50

# Check cluster health
docker compose exec temporal tctl cluster health

# Access UI
open http://localhost:8233
```

### Prometheus Metrics

Temporal exposes metrics on port 9090:

```bash
# View raw metrics
curl http://localhost:9090/metrics

# Metrics are automatically scraped by Prometheus
# View in Prometheus UI: http://localhost:9090
# View in Grafana: http://localhost:3001
```

Metrics include:

- Workflow execution counts and durations
- Task queue depths and processing rates
- Service health and resource usage
- Database connection pool stats

## Environment Configuration

| Service             | URL                             | Credentials                                         |
| ------------------- | ------------------------------- | --------------------------------------------------- |
| Temporal UI         | <http://localhost:8233>         | None                                                |
| Temporal gRPC       | localhost:7233                  | None                                                |
| Temporal Metrics    | <http://localhost:9090/metrics> | None                                                |
| Temporal PostgreSQL | localhost:5433                  | `temporal` / `temporal_dev_password_change_in_prod` |

## Configuration

### Environment Variables

Copy `.env.example` to `.env` and customize:

```powershell
cp .env.example .env
```

Default configuration assumes the shared Folium PostgreSQL container is running on the `south-drift-network` Docker network.

### Connecting Workers

Workers connect to Temporal server at `temporal:7233` (Docker network) or `localhost:7233` (host network).

**Docker Compose**:

```yaml
environment:
  - TEMPORAL_ADDRESS=temporal:7233
```

**Local Python Worker**:

```python
client = await Client.connect("localhost:7233")
```

## Database Management

### Reset Temporal State

```powershell
# Stop and remove all data
docker compose down -v

# Start fresh
docker compose up
```
