# Folium Offline Evaluation

## Purpose

Offline evaluation is a repeatable, pre-release qualification run against a
local, test, or staging system outside live user traffic. Its primary form
drives the deployed versioned API with anonymized fixtures and measures the
complete system before rollout.

## Invocation Modes

- **External staging API adapter:** the promotion gate. It exercises authentication,
  serialization, routing, persistence, workflow wiring, provider configuration,
  and output validation against the non-production deployment.

Every run records endpoint revision, environment, configuration fingerprint,
model identity, prompt/pipeline revision, and dataset/rubric/gate versions.
The evaluator remains external: it drives the deployed API and consumes
restricted, evaluation-safe evidence after the normal workflow is terminal.

## Architecture Decision: External System Evaluation

Folium evaluates agentic systems from outside their workflow boundary. An
evaluator seeds versioned anonymized evaluation data through approved APIs, invokes the
normal user-facing operation, waits for its terminal result, and reads a
restricted evaluation-safe evidence record. It does not call graph nodes or
provider functions directly, manufacture worker inputs, replace tools, or
reach into service persistence.

This choice is deliberate. A direct runner can be fast, but it duplicates
service-owned input assembly and bypasses authentication, serialization,
routing, persistence, orchestration, retry behavior, tools, and response
validation. It can pass while the deployed system is broken. The chart-review
direct runner was removed after the native `EncounterNarrative` source was
omitted from its real backend snapshot despite being available to the direct
path. Unit tests remain appropriate for deterministic pure primitives; system
quality evidence and promotion gates use the external adapter only.

For multi-step agent workflows, the evaluator still remains external. The
workflow emits typed, minimal trace events at approved decision and tool
boundaries, keyed by its durable run or review ID. The evaluator reads those
events after completion. This makes intermediate decisions evaluable without
letting evaluation code control the workflow.

## Pipeline Execution

The benchmark command accepts all runtime dependencies through explicit
configuration: target API URL, evaluation identity reference, dataset ID,
prompt/model revision, tracking URI, and timeout policy. It must not assume a
local Docker daemon, manually running model, developer database, or a fixed
endpoint.

Run it in three ways using the same immutable dataset and rubric:

- **Local:** author a fixture or diagnose a regression against the local
  deployed API and workflow.
- **On demand:** dispatch an evaluation pipeline for a selected prompt, model,
  or deployment revision.
- **Required gate:** run the staged API benchmark after each prompt/model change
  and before its rollout is eligible.

The pipeline creates or targets a disposable non-production stack, waits for
its health checks, runs the anonymized fixture lifecycle, uploads case artifacts
and aggregate metrics to MLflow, and reports the gate result to the change.
Infrastructure credentials remain in the pipeline environment; the runner gets
only its dedicated evaluation identity and configuration references. A failed
or inconclusive run blocks promotion and retains artifacts for review.

## Dataset And Evidence Contract

A committed dataset has a manifest with ID, immutable version, schema version,
anonymized-data declaration, file list, and checksums. Cases hold service-owned
seed inputs and expected observable properties. Annotations are append-only:
each records its ID, rubric version, authoring identity, timestamp, status, and
superseded annotation when corrected.

Every case artifact records validated output or terminal failure, evidence IDs,
stage timings, score details, and run metadata. MLflow receives aggregate
metrics, tags, and artifact links; committed datasets and annotation revisions
remain the durable source of truth.

## Performance Baseline

Report per-run count, minimum, median, $p95$, maximum, validation failures, and
pass rate. Preserve provider wall-clock time separately from queue delay,
workflow time, runner overhead, parsing, and scoring. Establish an initial warm
sequential baseline with identical dataset, model/provider configuration, and
hardware metadata. A small correctness benchmark does not establish capacity or
throughput.

## Promotion Gate

The generic gate returns `pass`, `fail`, or `inconclusive` from versioned
threshold policy. It blocks a revision from promotion when evidence fails, but
never authorizes clinical action. Automated promotion, LLM-as-judge, and
statistical significance require separate approved policy.
