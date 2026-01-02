# Audio Transcription Microservice

FastAPI microservice for audio transcription with **Abstract Provider Pattern**. Currently production-ready with self-hosted Whisper (HIPAA-compliant). Processes 1-3 second clinical voice notes in ~0.5-0.6 seconds.

## Overview

**What it does**: Accepts presigned audio URLs, downloads audio via HTTP, transcribes using faster-whisper, returns transcript JSON.

**Key Features**:

- **Storage-agnostic**: Works with MinIO/S3/Azure Blob presigned URLs
- **HIPAA-compliant**: Self-hosted Whisper keeps PHI on-premise (no BAA required)
- **Fast**: 0.5-0.6s processing for short voice notes
- **Provider Pattern**: Extensible design for AWS Transcribe/Azure Speech (planned)

**Current Status**: ✅ Production-ready with Whisper base model

---

## Quick Start

### Local Development (Docker Compose)

**Recommended**: Run entire stack with hot reload:

```bash
# From repo root
docker compose up
```

Services:

- Transcription: `http://localhost:8001`
- Backend: `http://localhost:8000`
- Frontend: `http://localhost:3000`
- MinIO: `http://localhost:9000`

**Docker watch** syncs code changes automatically (no rebuild needed for `.py` file edits).

### Standalone Service

```bash
cd services/transcribe

# Install with uv
uv pip install -e .[whisper]

# Set config
export TRANSCRIPTION_PROVIDER=whisper
export WHISPER_MODEL_SIZE=base
export WHISPER_DEVICE=cpu

# Run
uvicorn app.main:app --reload --port 8001
```

First startup downloads Whisper base model (~150MB, cached for subsequent runs).

---

## API Usage

### Transcribe Audio

```bash
curl -X POST http://localhost:8001/transcribe \
  -H "Content-Type: application/json" \
  -d '{
    "audio_url": "http://minio:9000/bucket/audio.webm?signature=...",
    "language_code": "en-US"
  }'
```

**Response**:

```json
{
  "transcript": "This is the transcribed text",
  "language_code": "en",
  "confidence": null,
  "segments": [
    {
      "start_time": 0.0,
      "end_time": 2.1,
      "text": "This is the transcribed text",
      "confidence": null,
      "speaker_label": null
    }
  ],
  "processing_time": 0.58,
  "job_id": null
}
```

### Health Check

```bash
curl http://localhost:8001/health
```

**Response**:

```json
{
  "status": "healthy",
  "provider": "whisper-base",
  "model": "base"
}
```

---

## Configuration

### Environment Variables| Variable | Default | Options | Description |
|----------|---------|---------|-------------|
| `TRANSCRIPTION_PROVIDER` | `whisper` | `whisper`, `aws`, `azure` | Active transcription provider |
| `WHISPER_MODEL_SIZE` | `base` | `tiny`, `base`, `small`, `medium`, `large` | Whisper model size |
| `WHISPER_DEVICE` | `cpu` | `cpu`, `cuda` | Processing device |
| `LOG_LEVEL` | `INFO` | `DEBUG`, `INFO`, `WARNING`, `ERROR` | Logging verbosity |

### Provider Selection (Future)

Switch providers via environment variable (currently only Whisper implemented):

```bash
# Self-hosted (HIPAA compliant) ✅ CURRENT
TRANSCRIPTION_PROVIDER=whisper

# AWS Transcribe (planned - requires BAA)
TRANSCRIPTION_PROVIDER=aws

# Azure Speech (planned - requires BAA)
TRANSCRIPTION_PROVIDER=azure
```

---

## Architecture

```
services/transcribe/
├── app/
│   ├── main.py              # FastAPI app (/transcribe, /health endpoints)
│   ├── config.py            # Settings (provider, model, device)
│   ├── models.py            # Pydantic schemas (request/response)
│   └── providers/
│       ├── base.py          # TranscriptionProvider ABC
│       ├── whisper.py       # faster-whisper implementation ✅
│       ├── factory.py       # Provider factory + singleton
│       ├── aws.py           # AWS Transcribe (planned)
│       └── azure.py         # Azure Speech (planned)
├── Dockerfile               # Multi-stage build (whisper/aws/azure)
├── docker-compose.yml       # Local dev config
└── pyproject.toml           # uv dependencies
```

**Pattern**: Abstract Provider Pattern with factory + singleton  
**Benefits**: Provider switching via config, consistent interface, testable

---

## Development

### Hot Reload

Docker watch mode enabled - edit `.py` files, changes sync automatically:

```bash
# Start with watch
docker compose up

# Edit app/providers/whisper.py
# Service reloads automatically (via --reload flag)
```

### Rebuild Triggers

Rebuild required only for:

- Dependency changes (`pyproject.toml`)
- Dockerfile changes
- Model switching (Whisper size)

```bash
docker compose build transcribe
```

### Debugging

View logs:

```bash
docker compose logs transcribe --follow
```

Logs include:

- 🎤 Audio download and file size
- 📊 Segment count and detected language
- 📝 Transcript preview (first 100 chars)
- ✅ Processing time

### Testing

```bash
# Unit tests (planned)
pytest tests/

# Integration test via curl
curl -X POST http://localhost:8001/transcribe \
  -H "Content-Type: application/json" \
  -d '{"audio_url": "http://minio:9000/..."}'
```

---

## Performance

**Whisper Base Model**:

- 1-second audio: ~0.5s processing
- 3-second audio: ~0.6s processing
- CPU usage: 80-100% (single-threaded)
- Memory: ~500MB (model loaded)

**Optimization Tips**:

- Use `tiny` model for speed (lower accuracy)
- Use `small`/`medium` for better accuracy (slower)
- GPU (`cuda`) for 5-10x speedup (requires NVIDIA hardware)

---

## Troubleshooting

### "Model not found" error

Model downloads on first use. Ensure internet access or pre-cache in Dockerfile.

### Slow processing

- Check CPU usage (should be 100% during transcription)
- Try smaller model (`tiny` instead of `base`)
- Consider GPU support (requires CUDA)

### Empty transcripts

- Check audio format (WebM supported, prefer WAV/MP3)
- Verify audio not corrupted (download manually, test with media player)
- Check logs for VAD filter warnings (currently disabled)

### Healthcheck failing

Docker HEALTHCHECK uses `HEAD /health`. Ensure service started (40s start period).

---

## Documentation

- **[SPEC.md](SPEC.md)**: Complete technical specification
- **[Dockerfile](Dockerfile)**: Multi-stage build details
- **[docker-compose.yml](docker-compose.yml)**: Local development config