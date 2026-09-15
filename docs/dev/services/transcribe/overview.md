# Transcription service

Folium keeps transcription in a focused service because audio processing has
different model-initialization, compute, and processing-time needs from
interactive clinical workflows. Keeping that work separate lets the backend
remain responsible for access, workflow state, and reviewable results.

Each new transcript replaces interaction note completely (with timestamp). This approach simplifies the user experience and aligns with clinical workflow priorities, it avoids duplicate accumulation, and ensures that the latest voice note is always the most relevant. As a trade-off, previous transcripts are lost.

## Provider and storage boundary

The service selects one configured provider for a running instance and receives
approved audio through a presigned URL. It can retrieve audio without carrying
the backend's storage credentials or depending on a particular object-storage
SDK. That preserves one transcription contract while allowing the storage and
deployment model to change independently.

The local provider is the current default. Azure and AWS transcription
providers remain planned and require explicit identity, network, data-residency,
cost, and validation work before they become supported options.

## Runtime behavior

The service exposes a transcription endpoint alongside health and metrics
endpoints. The local model cache is populated on first use and reused by later
runs. Voice-note workflows use Temporal when processing needs to continue
beyond the originating request.

See [service boundaries](../../architecture/service-boundaries.md) and
[Temporal runtime](../../operations/temporal-runtime.md) for the platform
rationale.
