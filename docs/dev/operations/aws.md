# Planned AWS deployment

AWS is folium's later planned hosted deployment target, following a validated
local/on-prem path and Azure hosted implementation. It is not a supported
deployment option today.

## Why AWS remains an option

An AWS deployment can fit organizations that already operate their identity,
networking, container platform, object storage, and monitoring in AWS. The
backend and focused services are separated so interactive workflows and
specialized processing workloads can be deployed and scaled for their own
operational needs.

## What a hosted implementation must decide

Moving to AWS changes more than where containers run. The implementation must
make environment promotion, identity and access control, private networking,
data residency, storage lifecycle, observability, and provider cost explicit.
Those decisions need validation before AWS is presented as a product capability.

Specific resource topologies, fixed capacity estimates, model choices, and
compliance claims are intentionally not prescribed here. They depend on the
customer environment and the implemented workload.

See [deployment order](../architecture/deployment-order.md) and
[CI/CD promotion](../operations/ci-cd-promotion.md) for the shared deployment
rules.
