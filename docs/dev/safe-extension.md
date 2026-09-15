# Safe extension

Extend Folium by preserving the bounded workflow and its evidence contracts.

## Before changing behavior

- Identify the owning service and contract.
- Add or update a synthetic fixture.
- Define deterministic validation and expected review flags.
- Decide which workflow and offline evaluation prove the change.
- Update the user guide only after the behavior is implemented and validated.

## Guardrails

- Never add arbitrary user code or unrestricted model tools.
- Never allow a worker to bypass backend ownership and source checks.
- Never use real patient data, credentials, or identifiable examples.
- Never describe draft output as diagnosis, treatment, or autonomous action.
- Keep broader retrieval, cloud providers, and cloud deployment explicitly
  planned until their evidence exists.
