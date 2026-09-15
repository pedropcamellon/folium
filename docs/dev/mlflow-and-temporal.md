# MLflow evidence and Temporal audit

The local agentic lane records evidence around draft generation rather than
performing autonomous clinical work.

## Evidence path

- Synthetic context identifies the exact input case.
- The bounded draft agent produces structured draft fields and source references.
- Validation records deterministic findings and review flags.
- Offline evaluation compares the result with committed synthetic cases.
- MLflow records comparable local runs with model, prompt, and dataset metadata.
- Temporal provides production-style orchestration, retries, correlation, and an
audit event before human review.

A low-confidence or validation-flagged result routes to review. These signals
are workflow attributes, not calibrated clinical risk scores.

## Local-first boundary

MLflow and the workflow evidence path must work locally without cloud credentials.
Azure and AWS providers, cloud deployment, and provider-specific performance
claims are planned until they have implementation and validation evidence.
