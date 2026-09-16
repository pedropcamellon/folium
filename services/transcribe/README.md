# Transcription service

This FastAPI service turns approved audio input into transcript data for
folium workflows. It is isolated from the backend because audio processing has
its own model initialization, compute, and scaling requirements.

## Run locally

Run the full platform from the repository root:

```bash
uv run folium
```

See the [local runtime guide](../../docs/dev/local-development.md) for
prerequisites and service controls.

For standalone troubleshooting only, install the service with the `whisper`
extra and run it on port `8001`. The service exposes `POST /transcribe` and
`GET /health`. The local model cache is populated on first use and reused by
later runs.

Azure and AWS transcription providers are planned, not current supported
runtime options. See the [service boundaries](../../docs/dev/architecture/service-boundaries.md)
and [Temporal runtime](../../docs/dev/operations/temporal-runtime.md) for the
operational rationale, or the [transcription service overview](../../docs/dev/services/transcribe/overview.md)
for its provider and storage boundaries.
