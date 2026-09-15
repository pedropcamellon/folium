# Frontend demo

Folium plans a public way to demonstrate its workflow experience without
exposing an application backend or creating a data-handling commitment.

## Decision

The demo will be a static frontend backed by committed fixture data. It is
separate from local and hosted full-stack deployments: inexpensive to share,
but not a representation of live integrations, worker processing, or backend
data behavior.

Connecting the demo to production-like services, accepting user data, or
presenting fixtures as live clinical records is out of scope.
