# CI/CD promotion

Folium keeps cloud promotion explicit because a deployment changes the
environment, data boundary, and operating responsibility of the platform.
Reusable provider workflows let Azure and AWS vary where they must, while the
build and approval stages remain consistent.

## Decision

Backend promotion is manually initiated with an environment selection and moves
through build, approval, optional infrastructure, and deployment stages. The
workflow structure favors a deliberate release over automatic cross-cloud
promotion.

This adds review and coordination to deployment work, but avoids silently
shipping a change into an environment with different identity, network, cost,
or data-residency constraints. Provider-specific workflow code is isolated,
not duplicated across the common promotion path.

See [deployment order](../architecture/deployment-order.md) for the sequence in
which local, Azure, and AWS deployment paths are considered.
