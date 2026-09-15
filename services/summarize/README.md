# Summarization service

This FastAPI service produces structured summaries from approved transcript
input. The clinical-note summarizer targets a SOAP layout. Provider
configuration is encapsulated by the service so the rest of folium uses a
stable typed contract rather than provider-specific SDKs.

## Run locally

Run the full platform from the repository root:

```bash
uv run folium
```

For standalone development, install the service with its required local
provider extra and run the application on port `8002`. The service exposes
`POST /summarize` and `GET /health`.

Provider-backed Azure and AWS deployments are planned, not current supported
runtime options. See the [service boundaries](../../docs/dev/architecture/service-boundaries.md)
and [summarization service overview](../../docs/dev/services/summarize/overview.md)
for the design rationale. Planned provider directions are documented for
[Azure](../../docs/dev/services/summarize/azure-provider.md) and
[AWS](../../docs/dev/services/summarize/aws-provider.md); see
[prompt design](../../docs/dev/services/summarize/prompt-design.md) for the
SOAP output and grounding goals, and [local model artifact](../../docs/dev/services/summarize/local-model.md)
for the verified local runtime baseline.
