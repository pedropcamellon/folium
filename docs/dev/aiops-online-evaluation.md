# Folium Online Evaluation

## Purpose

Online evaluation observes a served revision after its staging gate passes. It
is asynchronous evidence collection, never a benchmark executed within a live
user request and never an automatic approval path.

## Rollout Modes

- **Shadow:** runs approved observation without changing the user-visible draft
  or workflow result.
- **Canary:** serves an explicitly limited rollout with an immediate rollback
  path and required human review for chart-review outputs.

Neither replaces staged qualification. They verify that latency, validation, and
quality signals remain consistent once the model is served.

## Minimal Event And Labels

The runtime emits a non-sensitive event with correlation ID, service/model and
prompt/pipeline revisions, configuration fingerprint, timestamps, stage
durations, validation outcome, bounded failure category, and review disposition.
An asynchronous collector joins the event to delayed human annotations or
trusted outcome labels when available.

This produces separate operational performance, prediction-quality, and
drift/coverage views. For conventional ML, include feature-schema version,
model artifact digest, prediction, and later ground truth. For agents, include
policy revision, structured-validation result, source-reference outcome, and
human-review disposition.

## Data Boundary

Do not send raw patient content, prompts, transcripts, or unrestricted output
to MLflow or general telemetry. MLflow may hold aggregated monitoring snapshots
and artifact links; the approved event and versioned-label stores retain
auditable evidence. Retention, access, de-identification, and review policy
need approval before a real-world data path exists.

Drift and missing-label rates are review signals, not proof of quality
degradation, and never trigger autonomous clinical action.
