# folium

![folium](frontend/public/banner.png)

Folium is a modern clinical workflow platform built to reduce administrative
burden and help care teams focus on individualized, clinician-led care. It
combines clear workflow design, reviewable operations, and an on-prem-first
deployment model so teams retain control over their environment and data
boundaries.

Folium is not a complete EHR. It focuses on practical clinical-record workflows
that are easier to operate, validate, and extend responsibly.

## Explore Folium

- [Live documentation](https://pedropcamellon.github.io/folium/)
- [Supported workflows](https://pedropcamellon.github.io/folium/user-guide/)
- [Platform architecture](https://pedropcamellon.github.io/folium/dev/architecture/overview/)
- [Deployment models](https://pedropcamellon.github.io/folium/dev/architecture/deployment-modes/)
- [Developer guide](https://pedropcamellon.github.io/folium/dev/)

## Platform areas

- **Clinical workflows:** patient records, interactions, voice notes, and
  review surfaces designed for focused day-to-day work.
- **Secure operations:** on-prem-first deployment, explicit data boundaries,
  typed validation, and auditable workflow execution.
- **Focused services:** transcription and summarization workloads can evolve
  and scale independently from interactive application workflows.
- **Evidence and review:** evaluation, MLflow evidence, and Temporal audit
  context support informed human review.

## Planned capabilities

- A free, fixture-only static frontend demonstration.
- Hosted full-stack deployment, beginning with Azure and followed by AWS.
- Broader retrieval, confidence calibration, and dedicated local-serving
  performance work.

Planned capabilities are not current product features. Folium does not support
clinical diagnosis, treatment recommendations, autonomous action, or real
patient data in its local development and evaluation workflow.

## Local development

Folium's supported development path uses Docker Compose and the root runtime
command:

```bash
uv run folium
```

See the [local runtime guide](https://pedropcamellon.github.io/folium/dev/local-development/)
for prerequisites, service controls, and synthetic-data safeguards.
