# Service and contract boundaries

Folium is a monorepo containing the FastAPI backend, Next.js frontend, shared
contract primitives, and focused AI services. The backend owns patient scope,
validation, and data-boundary decisions. Workers receive approved typed inputs;
they do not receive database credentials or unrestricted chart search.

## Boundary rules

- Keep shared contracts stable and free of central business logic.
- Keep provider output behind strict typed transport validation.
- Keep patient and interaction ownership checks in the backend.
- Keep model prompts and provider-specific behavior inside the owning service.
- Use synthetic fixtures and deterministic validation for new agent behavior.

The chart-review worker may request a bounded set of prior interaction context.
The backend enforces the patient, source-field, active-interaction, term-count,
and result-count boundaries.

## Deferred contracts

Broad document retrieval, confidence calibration, dedicated local serving
performance, Azure/AWS providers, and cloud deployment remain planned. Do not
add documentation or UI workflows that imply those contracts are delivered.
