# PostgreSQL

Folium uses PostgreSQL for application data: clinical records, ownership
relationships, attachments metadata, and workflow-facing state. The backend
accesses it through asynchronous SQLAlchemy sessions, while Alembic manages
schema evolution.

## Why PostgreSQL

Clinical workflows depend on related records and explicit ownership boundaries.
PostgreSQL provides relational constraints and transactions that keep those
relationships consistent as a workflow creates or updates related data.

The backend keeps persistence behind repositories and services, so routes do
not embed database behavior. That allows the data model and schema migrations to
evolve without changing the API's responsibility boundaries.

## Separate from Temporal

PostgreSQL is also used by Temporal, but in a separate database owned by the
workflow engine. Temporal persistence stores orchestration state such as
workflow progress, task execution, and retries. It is not the application's
clinical-record database and services do not use it as a user-data store.

See [backend layers](layers.md) for the route, service, and repository boundary,
and [Temporal runtime](../operations/temporal-runtime.md) for workflow
orchestration.
