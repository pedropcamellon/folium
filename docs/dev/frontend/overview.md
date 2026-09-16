# Frontend boundaries

The frontend is a Next.js application for task-focused workflow and review
surfaces. It presents backend-supported work to a user; it does not own
clinical workflow policy or act as an independent product backend.

## App Router and typed UI

Next.js App Router provides the application shell and route structure.
Interactive workflow surfaces are client components, while reusable UI
primitives and shared TypeScript types keep forms, tables, and dialogs
consistent. Types must follow the backend API models so a field-name or data
shape change is corrected at the boundary rather than patched in a component.

## One API boundary, no BFF

The browser calls FastAPI directly through `src/lib/api.ts`. That module owns
the public base URL, endpoint construction, authenticated requests, JSON
parsing, and the unauthenticated redirect. Domain services and hooks use these
helpers instead of embedding URLs or request mechanics in components.

This keeps the local stack small and makes the API contract visible. A
backend-for-frontend layer would add another deployable service without a
current requirement. Add one only when it provides a concrete capability that
the API and client boundary cannot safely provide.

## Task hooks and visible states

SWR supplies cached reads and revalidation. Task hooks combine that data access
with mutation actions and expose a small workflow-facing interface to the
orchestrating component. Presentational components receive data, state, and
event handlers rather than creating their own requests.

`usePatients` is the representative pattern: it owns the patient read,
mutations, refresh after a change, submission state, and request error. The
section component composes the hook with a table and dialog; those
presentational components do not need to know how a request is made.

Use a typed enum when a workflow has meaningful stages. `DataStatus` describes
the read state as idle, loading, success, or error. `AudioState` describes
recording and submission stages, including loaded, recording, recorded,
submitting, submitted, and error. Explicit states prevent contradictory
boolean flags and give the UI a clear loading or failure condition when the API
is unavailable.

## Types and request errors

Use shared TypeScript types at the API-facing edge and keep them aligned with
the backend's request and response models. Avoid `any` in new workflow code:
an explicit form, API, or component-props type makes a contract mismatch
visible before it becomes a browser-only failure.

`apiRequest` owns authenticated raw requests, and `apiJson` owns successful
JSON parsing and failed-response rejection. Hooks can then decide how a
workflow reports a recoverable error, while components render that state. This
separation keeps request mechanics consistent without treating every server
failure as a UI concern.

## Authorization and policy

The client uses the signed-in user's permissions to decide which actions to
offer, improving usability. It is not the authorization boundary: FastAPI must
validate identity, permissions, input, and workflow rules for every request.
The frontend must not reproduce clinical policy or infer that a hidden action
is prohibited.

See [backend layers](../backend/layers.md) for the server-side ownership model
and [service boundaries](../architecture/service-boundaries.md) for the
platform-wide boundary map.
