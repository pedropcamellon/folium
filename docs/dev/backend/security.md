# Backend security boundaries

Folium treats the backend as the boundary between a caller, clinical workflow
policy, persistence, and focused services. Security controls are applied at the
boundary where they can be validated and audited rather than being delegated to
the frontend or a worker.

## Access and authorization

Routes require an active authenticated user and enforce named permissions
through FastAPI dependencies. The permission check is part of the route
contract, so a service does not assume that a caller was authorized merely
because a request reached it. Internal workflow endpoints use a separate,
constant-time token comparison before accepting worker requests.

## Validated inputs and configuration

Pydantic models validate untrusted API input before it reaches workflow or
persistence code. Required runtime settings, including database, storage, and
internal-workflow credentials, are validated at startup. Typed boundaries keep
unexpected values from silently becoming workflow or database behavior.

## Browser and service boundaries

CORS uses configured allowed origins rather than accepting every browser origin.
Focused services receive approved, scoped inputs instead of direct application
database access. Correlation and structured logging support review of requests
and workflow activity without making logs a substitute for authorization.

## Deployment responsibility

This page describes implemented application boundaries, not a compliance claim.
Deployment-specific controls such as network isolation, secret storage,
encryption, retention, and monitoring configuration must be selected and
validated for the environment where folium runs.

See [backend layers](layers.md), [storage providers](storage.md), and
[service boundaries](../architecture/service-boundaries.md) for the related
ownership boundaries.
