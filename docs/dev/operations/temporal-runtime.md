# Temporal runtime

Some workflows take longer than an interactive request and need retry,
correlation, and a reviewable record of what happened.

Temporal is used for durable orchestration. The backend initiates typed work and
workers process only approved, scoped inputs before returning validated results.

## Temporal persistence

Temporal uses its own PostgreSQL database for workflow-engine state, including
execution progress, task processing, and retries. It is separate from the
application PostgreSQL database that stores user-facing clinical records and
workflow-owned application data. This keeps orchestration internals from
becoming an alternate clinical-record store.

PostgreSQL is an appropriate persistence baseline for the current local scale:
it keeps Temporal state durable without introducing another data platform. A
change in throughput, retention, or availability requirements should be
measured before adding more operational complexity.

## Interactive requests and durable work

An interactive endpoint can return a direct, permission-scoped result when the
work fits the request lifecycle. For longer-running workflows, the backend first
persists the request state, starts a Temporal execution, and returns the
workflow identity. The client can then inspect workflow status while the work
continues independently of the original request.

Voice-note processing and chart review use this durable path. It gives the
platform an explicit record of queued work, retries, failures, and the result
that must be reviewed, without holding an interactive request open.

Temporal adds a runtime dependency and operational overhead, but makes retries,
audit context, and human review routing explicit instead of embedding them in
ad hoc background tasks.

!!! note "Runtime boundary"

    Workers do not have unbounded access to clinical data, and Folium does not
    support arbitrary user-defined workflow code or provider-specific
    orchestration.
