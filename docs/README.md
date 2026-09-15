![Folium](assets/banner.png){ .folium-banner }

# Modern clinical workflows, built for control

Folium helps teams run clear, reviewable clinical-record workflows without
turning day-to-day operations into a sprawling system project. Its on-prem-first
architecture keeps security, data boundaries, and operational control in view
from the start.

Folium is not a complete EHR. It focuses on practical clinical workflows that
are easier to operate, validate, and extend responsibly.

## Mission

Reduce administrative burden so care teams can devote more time to thoughtful,
individualized, clinician-led care.

## Vision

Make modern clinical operations easier to run: secure by design, flexible in
where they are deployed, and clear enough that every workflow remains
reviewable as the platform grows.

## Designed for how teams operate

**Control the data boundary**

Run Folium in your own environment when sovereignty, network constraints, or
operational control matter most.

**Keep work reviewable**

Validation, evaluation evidence, and workflow audit context support clear
human review rather than opaque automation.

**Evolve without platform sprawl**

Focused services can scale for their own workload while stable shared contracts
keep the platform coherent.

## Start here

- [Explore supported workflows](user-guide/index.md)
- [Understand the platform architecture](dev/architecture/overview.md)
- [Choose a deployment model](dev/architecture/deployment-modes.md)

## For builders

Folium provides a supported local path for development and evaluation. Start
with the [developer guide](dev/index.md), then run the local runtime from the
repository root:

```bash
uv run folium
```

Use only synthetic data in local development and evaluation. Hosted Azure and
AWS deployments are planned configuration targets, not current product
capabilities.
