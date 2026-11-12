# Infrastructure

Infrastructure is organized by deployment target and workload:

- [`demo/`](demo/) is the isolated, synthetic-data-only mock frontend demo. It
  provisions Free F1 App Service with built-in Node hosting and has its own
  Terraform state and release pipeline.
- [`azure/`](azure/) contains the full Folium Azure application infrastructure
  and reusable Azure modules. It is not the lightweight demo deployment.
- [`aws/`](aws/) contains the planned AWS deployment configuration.

The local Docker Compose runtime remains the supported path for development and
evaluation. Hosted deployment choices must preserve explicit data boundaries,
identity controls, operational visibility, and reviewable workflows.

See [deployment modes](../docs/dev/architecture/deployment-modes.md) and
[deployment order](../docs/dev/architecture/deployment-order.md) for the product
and architecture rationale.
