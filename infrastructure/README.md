# Infrastructure

Infrastructure is organized by deployment target and workload:

- [`demo/`](demo/) provisions the isolated synthetic-data frontend on Azure
  Static Web Apps Free, using separate remote state. It contains no container
  registry, running application server, or backend resources.
- [`azure/`](azure/) contains the full Folium Azure application infrastructure
  and reusable Azure modules. It is not the lightweight demo deployment.
- [`aws/`](aws/) contains the planned AWS deployment configuration.

The local Docker Compose runtime remains the supported path for development and
evaluation. Hosted deployment choices must preserve explicit data boundaries,
identity controls, operational visibility, and reviewable workflows.

See [deployment modes](../docs/dev/architecture/deployment-modes.md) and
[deployment order](../docs/dev/architecture/deployment-order.md) for the product
and architecture rationale.
