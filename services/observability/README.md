# Observability Stack

Prometheus and Grafana for monitoring SouthDrift services.

## Services

- **Prometheus**: Metrics collection and storage
  - URL: http://localhost:9090
  - Scrapes metrics from backend, transcription, summarization, and Temporal services

- **Grafana**: Metrics visualization and dashboards
  - URL: http://localhost:3001
  - Default credentials: `admin` / `admin`
  - Pre-configured Prometheus datasource

## Usage

Start the observability stack with the main docker-compose:

```bash
docker compose up prometheus grafana
```

Or start all services:

```bash
docker compose up
```

## Adding Metrics to Services

### FastAPI (Backend, Transcription, Summarization)

Install prometheus client:

```bash
uv add prometheus-client
```

Add to your FastAPI app:

```python
from prometheus_client import Counter, Histogram, generate_latest
from starlette.middleware.base import BaseHTTPMiddleware

# Metrics
REQUEST_COUNT = Counter('http_requests_total', 'Total HTTP requests', ['method', 'endpoint', 'status'])
REQUEST_DURATION = Histogram('http_request_duration_seconds', 'HTTP request duration', ['method', 'endpoint'])

@app.get("/metrics")
async def metrics():
    return Response(generate_latest(), media_type="text/plain")
```

## Dashboard Examples

Check the `provisioning/dashboards/` directory for pre-configured dashboards.

## Configuration

- `prometheus.yml`: Scrape configuration
- `provisioning/datasources/`: Grafana datasource configuration
- `provisioning/dashboards/`: Dashboard provisioning configuration
