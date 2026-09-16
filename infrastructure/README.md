# Infrastructure

Infrastructure configuration supports folium's local-first deployment strategy.
The local Docker Compose runtime is the supported path for development and
evaluation. Azure and AWS configuration is retained as planned hosted-deployment
work, not as a currently supported product offering.

Hosted deployment choices must preserve the platform's explicit data boundaries,
identity controls, operational visibility, and reviewable workflow behavior.
See [deployment modes](../docs/dev/architecture/deployment-modes.md) and
[deployment order](../docs/dev/architecture/deployment-order.md) for the product
and architecture rationale.
