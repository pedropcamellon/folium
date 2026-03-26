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

- **Temporal Server**: Workflow orchestration engine (port 7233)
- **Temporal UI**: Web interface for monitoring workflows (port 8233)

Temporal reuses the shared PostgreSQL container from `../../docker-compose.database.yml` instead of running its own database.

## Usage Patterns

### 1. Standalone Infrastructure (this folder)

Run Temporal infrastructure only, develop workers separately:

```powershell
cd functions/temporal
docker compose up
```

Use this when:

- Running workers directly via `uv run worker.py` (not containerized)
- Debugging individual workers in VS Code
- Testing Temporal server configuration

### 2. Full Stack Orchestration

Run Temporal + all workers together:

```powershell
cd functions
docker compose up --watch
```

Use this for:

- End-to-end integration testing
- Simulating production-like environment
- Testing inter-service communication

### 3. Service Isolation

Run Temporal + specific worker:

```powershell
cd functions/extract-sq-ft
docker compose up --watch
```

Use this for:

- Focused service development
- Quick iteration on single service
- Service-specific testing

## Accessing Services

| Service | URL | Credentials |
|---------|-----|-------------|
| Temporal UI | <http://localhost:8233> | None |
| Temporal gRPC | localhost:7233 | None |
| PostgreSQL | localhost:5432 | `southdrift` / `dev_password_change_in_prod` |

## Configuration

### Environment Variables

Copy `.env.example` to `.env` and customize:

```powershell
cp .env.example .env
```

Default configuration assumes the shared SouthDrift PostgreSQL container is running on the `south-drift-network` Docker network.

### Connecting Workers

Workers connect to Temporal server at `temporal:7233` (Docker network) or `localhost:7233` (host network).

**Docker Compose**:

```yaml
environment:
  - TEMPORAL_ADDRESS=temporal:7233
networks:
  - temporal-network
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
