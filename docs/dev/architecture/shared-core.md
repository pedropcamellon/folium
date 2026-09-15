# Shared core

The backend and focused services need a reliable way to share typed contracts
and small runtime utilities without duplicating them or coupling every service.

## Decision

`folium-core` is limited to stable contracts and pure primitives used by at
least two consumers. Each application or service retains its own workflow and
business rules.

This can leave purposeful duplication near the owning service, but prevents a
shared package from becoming a hidden platform layer that is hard to change
safely. Centralizing business logic, provider integrations, persistence, or
workflow policy in `folium-core` is rejected.