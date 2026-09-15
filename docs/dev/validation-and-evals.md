# Validation and offline evaluation

Every agent change should be checked at the narrowest useful boundary first,
then exercised through the relevant workflow.

## Validation layers

1. Use typed request and response contracts at service boundaries.
2. Run deterministic validation for required fields, allowed sources, and review
   flags.
3. Exercise the backend and worker path with synthetic fixtures.
4. Run focused E2E flows when the change crosses the browser workflow.
5. Record failures and unsupported cases as evaluation evidence.

## Offline evaluation

The chart-review benchmark evaluates synthetic cases for completeness,
unsupported claims, source references, latency, and validation failures. It is
an evidence surface for draft support, not a clinical safety certification.

Run the repository's focused tests from the owning package or service. Keep
fixtures synthetic and avoid credentials, personal names, or real patient data.

## Planned evaluation work

Confidence calibration, broader retrieval quality, and dedicated local serving
performance require additional benchmark evidence. Until delivered, document
them as planned rather than as current behavior.
