# Deployment modes

Folium is designed for teams that need to choose where their reviewable
workflows run and where their synthetic evaluation evidence is retained. The
product has two deployment models: self-hosted/on-prem and hosted full stack.

## Self-hosted and on-prem

Self-hosting keeps the platform, its model runtime, and its data boundary under
the customer's control. It is the right starting point for organizations with
strict data-sovereignty requirements, constrained network access, or a policy
to keep their workflow runtime inside their own environment.

Docker Compose plus `uv run folium` is the supported local deployment and
evaluation path. It uses synthetic data and works without cloud credentials.
This is where workflow behavior and MLflow evidence are validated first.

## Hosted full stack

Hosted deployment is for teams that prefer managed infrastructure and a cloud
operating model. Folium's architecture is designed to be portable across Azure
and AWS, allowing a hosted deployment to align with an existing cloud estate,
identity model, networking controls, and monitoring practices.

Azure is the first planned hosted target, followed by AWS. Neither hosted path
is currently a supported deployment option; each requires explicit
implementation and validation before it can handle any non-synthetic data.
Hosted operation introduces cloud-provider cost, network egress, identity, and
data-residency considerations that a self-hosted deployment can avoid.

## Planned: free static demo

A free static frontend demonstration is planned, not currently available. It
will use fixture data only and must never imply that audio processing,
evaluation, or backend data services are available.

See [deployment order](deployment-order.md) for the tradeoffs.
