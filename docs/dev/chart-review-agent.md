# Chart Review Agent Lessons

## Local Operations

Run backend maintenance commands through the root Compose services while the
local stack is running. This preserves the API's container image, injected
configuration, and Docker-network dependencies.

```bash
docker compose exec -T folium-backend python -m app.clear_data
docker compose exec -T folium-backend python -m app.seed_db
```

Use `folium-postgres` for direct database inspection. Direct host commands are
development fallbacks, not the standard operational path.

## Bounded History Retrieval

The chart-review worker has no database credentials or unrestricted chart
search. It can make one internal HTTP request for prior interaction context.
The request contains the active patient and interaction identifiers, one to
three short agent-provided search terms, and a backend-enforced result cap.

The backend owns every data-boundary decision: it verifies that the active
interaction belongs to the patient, excludes that interaction, searches only
approved prior interaction text blocks, and returns at most three typed source
chunks. It does not accept SQL, source identifiers, arbitrary field names, or
unbounded query text. When no approved block matches, it returns no history.

Historical document retrieval remains deferred until it has a separately
evaluated extraction contract.

## Contract Failures

Treat provider JSON as a strict transport contract. The history-decision output
is either an empty `search_terms` list or a bounded list of concise terms. An
unknown key such as the retired `history_category` field is a validation error,
not an implicit decision to skip retrieval.

Final chart-review citations are validated against the exact active and
approved-history source IDs supplied to the model. Never substitute a nearby
source ID when a provider response cites an unavailable block.
