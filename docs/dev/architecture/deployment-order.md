# Deployment order

Folium can be self-hosted or later run as a hosted full stack. Those modes have
different operating costs, data boundaries, and support requirements.

## Decision

Validate the local, on-prem deployment path first. Azure is the first planned
hosted target; AWS follows after that path is implemented and validated.

This sequence delays cloud convenience, but keeps early operation predictable
and establishes evidence before taking on cloud identity, networking, residency,
and provider-cost concerns. Parallel Azure and AWS product deployments,
provider-specific workflow forks, and default cloud hosting are deferred.