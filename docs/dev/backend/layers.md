# Backend layers

The FastAPI backend separates HTTP handling, workflow policy, and persistence
so a clinical workflow can change without turning every route into a database
or orchestration implementation.

## Route layer

Routes receive requests, apply the API contract, enforce the relevant
permission, and return HTTP responses. FastAPI dependency injection supplies
the services a route needs. Routes stay thin so HTTP-specific concerns do not
become workflow policy.

## Dependency composition

Folium uses FastAPI's built-in dependency injection rather than an additional
container framework. Dependencies build request-scoped collaborators in order:
database session, repository, then service. This keeps dependencies visible at
the route boundary and makes services easier to test with focused substitutes.

## Service layer

Services coordinate the workflow: they apply business and ownership rules,
compose repository and focused-service calls, and decide when durable work must
be started. This is where the backend protects the workflow from being shaped
by UI or persistence details.

## Repository layer

Repositories keep SQLAlchemy queries, persistence mapping, and loading choices
near the data model. They provide consistent asynchronous data access while the
calling service retains workflow decisions and transaction ownership.

## Typed boundaries

Pydantic models validate untrusted API input and define the response contract.
Folium prefers typed models or dataclasses for internal workflow payloads rather
than passing unstructured dictionaries across layers. Those shapes make required
fields, ownership context, and validation expectations explicit.

`TypedDict` remains useful where a dictionary-shaped external protocol is the
right fit, such as a provider message payload. It is not a substitute for runtime
validation at an API boundary or for a durable domain/workflow contract.

This separation adds a small amount of indirection, but it makes the backend
easier to test and change. It also makes the ownership of HTTP behavior,
clinical workflow policy, and database behavior explicit.

See [repository layer](repository-layer.md) for the repository contract and
[service boundaries](../architecture/service-boundaries.md) for platform-wide
ownership.
