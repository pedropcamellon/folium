# Structured Logging & Audit Trail

SouthDrift uses structured JSON logging with correlation IDs for end-to-end request tracing and audit fields for HIPAA compliance.

## Architecture

- **JSON Logs**: All logs output as JSON for structured querying
- **Correlation IDs**: Unique ID per request, spans all services
- **Audit Fields**: `user_id`, `patient_id`, `action` on every audit log
- **Loki**: Log aggregation (queries in Grafana)
- **Promtail**: Ships container logs to Loki

## Usage

### Basic Logging

```python
from app.core.logging import setup_structured_logging

logger = setup_structured_logging("my-service")

logger.info("Processing request", extra={"request_id": "123", "status": "started"})
logger.error("Failed to process", extra={"error_code": "DB_TIMEOUT"})
```

Output:

```json
{
  "timestamp": "2026-04-06T09:30:00.123Z",
  "level": "INFO",
  "logger": "root",
  "message": "Processing request",
  "service": "my-service",
  "correlation_id": "a1b2c3d4-...",
  "request_id": "123",
  "status": "started"
}
```

### Audit Logging

For HIPAA compliance, use `.audit()` for actions involving patient data:

```python
logger.audit(
    action="patient_record_accessed",
    user_id="user_123",
    patient_id="patient_456",
    method="GET",
    endpoint="/api/v1/patients/456"
)
```

Output includes `audit=true` flag for filtering:

```json
{
  "timestamp": "2026-04-06T09:30:00.123Z",
  "level": "INFO",
  "message": "AUDIT: patient_record_accessed",
  "service": "backend",
  "correlation_id": "a1b2c3d4-...",
  "audit": true,
  "action": "patient_record_accessed",
  "user_id": "user_123",
  "patient_id": "patient_456",
  "method": "GET",
  "endpoint": "/api/v1/patients/456"
}
```

### Correlation IDs

Correlation IDs are automatically managed by middleware:

```python
from app.core.logging import get_correlation_id

# Get current request's correlation ID
correlation_id = get_correlation_id()

# Pass to external service calls
headers = {"X-Correlation-ID": correlation_id}
response = await httpx.get(url, headers=headers)
```

Frontend should include correlation ID in error reports.

### End-to-End Tracing

1. Request enters backend → correlation ID generated
2. Backend logs: `correlation_id=abc123`
3. Backend calls transcription service with `X-Correlation-ID: abc123`
4. Transcription service logs: `correlation_id=abc123`
5. Workflow started: `correlation_id=abc123`

Query in Grafana: `{correlation_id="abc123"}` → see entire request flow

## Compliance Queries

### Who accessed patient X?

```logql
{audit="true"} | json | patient_id="patient_456"
```

### What happened during this request?

```logql
{correlation_id="a1b2c3d4-..."}
```

### Show admin actions in last 24h

```logql
{audit="true"} | json | action=~".*_deleted|.*_created" | user_id=~"admin_.*"
```

### Failed transcriptions

```logql
{service="transcribe", level="ERROR"}
```

## Grafana Dashboards

Visit http://localhost:3001 (admin/admin):

1. **SouthDrift Audit & Logs**: Audit trail, errors, service logs
2. **SouthDrift Service Health**: Metrics (requests, latency, errors)
3. **MinIO**: Storage metrics

## Adding Audit Logging to New Endpoints

```python
from fastapi import Depends
from app.core.logging import setup_structured_logging
from app.dependencies import get_current_user

logger = setup_structured_logging("backend")

@router.get("/patients/{patient_id}")
async def get_patient(
    patient_id: str,
    current_user = Depends(get_current_user)
):
    # Log audit event
    logger.audit(
        action="patient_record_accessed",
        user_id=current_user.id,
        patient_id=patient_id,
        method="GET",
        endpoint=f"/api/v1/patients/{patient_id}"
    )

    # ... business logic
```

## Best Practices

1. **Always audit patient data access**: Read, create, update, delete
2. **Include user context**: Who performed the action
3. **Log errors with context**: Include IDs, operation attempted
4. **Use correlation IDs**: For tracing across services
5. **Don't log sensitive data**: PHI, passwords, tokens

## Development

View logs in terminal:

```bash
docker compose logs -f backend
```

Or in Grafana: http://localhost:3001 → Explore → Loki → `{project="south-drift"}`

---

2026-04-06 09:30
