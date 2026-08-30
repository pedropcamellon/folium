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

## Future Retrieval Quality

The current graph uses a one-step ReAct-style decision: given the active
interaction, the model either returns bounded `search_terms` or skips the
lookup. This keeps the runtime constrained, but the decision can be locally
myopic. For example, it may request a fact already present in the active
transcript, or choose an overly specific phrase that cannot match a prior
approved block.

A future plan-then-act design should remain bounded. A planning step first
names the active-context factual gap and permitted evidence scope. A separate
acting step then supplies one to three concise lexical search terms. The
backend continues to enforce patient scope, approved fields, active-interaction
exclusion, source-block cap, and exact returned provenance. Planning must not
authorize diagnosis, treatment, autonomous action, arbitrary queries, or extra
retrieval rounds.

Evaluate this policy through the synthetic offline benchmark in task #39, not
by adding backend synonym maps or fallback search. Benchmark cases should score
redundant, irrelevant, overly broad, overly specific, and lexically grounded
terms across prior interactions. Historical document retrieval is a separate
future evaluation track: it requires an approved extraction contract and
benchmark evidence before the runtime may search document-derived blocks.

## Contract Failures

Treat provider JSON as a strict transport contract. The history-decision output
is either an empty `search_terms` list or a bounded list of concise terms. An
unknown key such as the retired `history_category` field is a validation error,
not an implicit decision to skip retrieval.

Final chart-review citations are validated against the exact active and
approved-history source IDs supplied to the model. Never substitute a nearby
source ID when a provider response cites an unavailable block.
