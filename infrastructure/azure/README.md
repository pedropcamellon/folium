# Full application - Azure infrastructure

This directory contains Terraform for deploying the full Folium application
to Azure, including backend services and shared Azure modules. It does not
contain the small synthetic-data mock demo; that separate target lives in
[`../demo/`](../demo/).

This full-stack configuration is not the demo deployment and can provision
additional services and costs. Review its identity, networking, data residency,
and operational-cost decisions before use.

See the [deployment modes](../../docs/dev/architecture/deployment-modes.md) and
[deployment order](../../docs/dev/architecture/deployment-order.md) for context.
