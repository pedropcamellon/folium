![Folium](assets/banner.png){ .folium-banner }

# Modern clinical workflows

Folium is an in-progress personal engineering sandbox. It explores how clearer,
reviewable clinical-record workflows might reduce administrative burden so care
teams can spend more time on thoughtful, individualized, clinician-led care.

It is not a complete EHR or a production clinical system. The current work
focuses on practical workflow experiments that are easier to operate, validate,
and extend responsibly.

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
