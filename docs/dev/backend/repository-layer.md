# Repository layer

Repositories keep SQLAlchemy data access separate from the backend's workflow
and validation policy. They work with asynchronous database sessions and share
a structural contract, so services can depend on consistent data-access behavior
without requiring a common inheritance tree.

## Why this boundary exists

The separation keeps database queries, persistence mapping, and loading choices
close to the data model. Services remain responsible for clinical workflow
rules, while API models validate data at the application boundary. Transaction
ownership is explicit at the calling boundary rather than hidden behind a
generic repository API.

This adds a layer between services and the ORM, but it makes data access easier
to test, change, and inspect. It also reduces the chance that database-specific
choices leak into routes or workflow logic.

See [service boundaries](../architecture/service-boundaries.md) for the broader
backend ownership model.
