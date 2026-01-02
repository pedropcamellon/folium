# Clinical Summarization Service

FastAPI microservice for generating structured clinical summaries from transcripts using local LLMs or cloud providers.

## Quick Start

### Docker Compose (Recommended)

```bash
# 1. Download MediPhi-Clinical GGUF model (specialized for clinical NLP)
mkdir -p models
cd models
# Q4_K_M quantization (2.5GB, fast & recommended)
curl -L -O https://huggingface.co/mradermacher/MediPhi-Clinical-GGUF/resolve/main/MediPhi-Clinical.Q4_K_M.gguf
mv MediPhi-Clinical.Q4_K_M.gguf model.gguf
cd ..

# 2. Start service
docker compose up

# 3. Test API
curl -X POST http://localhost:8002/summarize \
  -H "Content-Type: application/json" \
  -d '{"transcript": "Patient reports chest pain for 2 days..."}'
```

### Local Development

```bash
# Install dependencies with uv
pip install uv
uv pip install -e .

# Set environment variables
export SUMMARIZATION_PROVIDER=local
export LOCAL_MODEL_PATH=/path/to/model.gguf

# Run service
uvicorn app.main:app --reload --port 8002
```

## Configuration

| Environment Variable | Default | Description |
|---------------------|---------|-------------|
| `SUMMARIZATION_PROVIDER` | `local` | Provider: `local`, `openai`, `bedrock`, `azure` |
| `LOCAL_MODEL_PATH` | None | Path to GGUF model file (required for local) |
| `LOCAL_MODEL_NAME` | `llama-3-8b-instruct` | Model name for logging |
| `LOCAL_N_CTX` | `4096` | Context window size |
| `LOCAL_TEMPERATURE` | `0.3` | Generation temperature (0.0-1.0) |
| `LOCAL_MAX_TOKENS` | `500` | Max tokens to generate |
| `OPENAI_API_KEY` | None | OpenAI API key (if using OpenAI) |
| `CORS_ORIGINS` | localhost URLs | Allowed CORS origins |

## API Usage

### POST /summarize

Generate structured SOAP note from clinical transcript.

**Request**:

```json
{
  "transcript": "Patient reports chest pain for 2 days. Pain is sharp, worse with deep breathing. No fever. Vital signs stable. Heart sounds normal. Likely costochondritis. Plan: NSAIDs, follow-up in 1 week if not improved.",
  "interaction_type": "consultation",
  "format": "soap",
  "language": "en"
}
```

**Response**:

```json
{
  "summary": "CC: Chest pain for 2 days | Likely costochondritis | Plan: NSAIDs, follow-up in 1 week",
  "structured_data": {
    "chief_complaint": "Chest pain for 2 days",
    "subjective": "Patient reports sharp pain, worse with deep breathing. No fever.",
    "objective": "Vital signs stable. Heart sounds normal.",
    "assessment": "Likely costochondritis",
    "plan": "NSAIDs, follow-up in 1 week if not improved",
    "clinical_tags": ["chest-pain", "costochondritis"],
    "icd_codes": ["M94.0"],
    "action_items": ["Prescribe NSAIDs", "Schedule follow-up in 1 week"]
  },
  "processing_time": 3.45,
  "model_used": "llama-3-8b-instruct",
  "provider": "local"
}
```

### GET /health

Health check endpoint.

**Response**:

```json
{
  "status": "healthy",
  "provider": "local",
  "model": "llama-3-8b-instruct"
}
```

## Architecture

```
┌─────────────┐
│   Backend   │ ──────────────┐
└─────────────┘               │
                              ▼
                    ┌──────────────────┐
                    │   Summarize API  │
                    │   (FastAPI)      │
                    └──────────────────┘
                              │
                              ▼
                    ┌──────────────────┐
                    │ Provider Factory │
                    └──────────────────┘
                              │
        ┌─────────────────────┼─────────────────────┐
        ▼                     ▼                     ▼
┌───────────────┐   ┌───────────────┐   ┌───────────────┐
│ Local LLM     │   │ OpenAI        │   │ AWS Bedrock   │
│ (llama.cpp)   │   │ (Planned)     │   │ (Planned)     │
└───────────────┘   └───────────────┘   └───────────────┘
```

**Abstract Provider Pattern**: All providers implement `SummarizationProvider` ABC. Factory selects provider based on `SUMMARIZATION_PROVIDER` environment variable.

## Development

### Project Structure

```
services/summarize/
├── app/
│   ├── main.py              # FastAPI application
│   ├── config.py            # Settings
│   ├── models.py            # Pydantic schemas
│   ├── prompts.py           # Prompt templates
│   └── providers/
│       ├── __init__.py      # Factory
│       ├── base.py          # ABC
│       ├── local.py         # Local LLM
│       ├── openai.py        # OpenAI (stub)
│       ├── bedrock.py       # AWS (stub)
│       └── azure.py         # Azure (stub)
├── tests/
├── Dockerfile               # Multi-stage build
├── docker-compose.yml       # Local dev
└── pyproject.toml          # Dependencies
```

### Hot Reload

Docker watch mode automatically reloads on code changes:

- `./app` directory synced to container
- Rebuild triggered on `pyproject.toml` changes

### Testing

```bash
# Install dev dependencies
uv pip install -e ".[dev]"

# Run tests
pytest tests/

# With coverage
pytest --cov=app tests/
```

## Recommended Models

| Model | Size | Context | Speed | Clinical Accuracy | Use Case |
|-------|------|---------|-------|-------------------|----------|
| **🏆 MediPhi-Clinical** | 2.5GB (Q4) | 128k | Fast | Excellent | **Production (Recommended)** |
| Llama 3.1 8B Instruct | 5GB | 8k | Medium | Good | General purpose |
| Mistral 7B Instruct | 4GB | 8k | Medium | Good | General purpose |
| Phi-3 Mini | 2GB | 4k | Fast | Medium | Development |

**Why MediPhi-Clinical?**

- Specialized for clinical NLP tasks (fine-tuned on PubMed, clinical notes, medical coding)
- Smaller size (2.5GB vs 5GB) with superior clinical performance
- **Outperforms GPT-4 on ICD-10 coding by 14%** (68.7% vs 54.7%)
- 128k context window (handles long clinical documents)
- MIT licensed, HIPAA-compliant (local inference)
- Based on Phi-3.5-mini-instruct (3.8B params)

**Download GGUF Models**:

- MediPhi: [mradermacher/MediPhi-Clinical-GGUF](https://huggingface.co/mradermacher/MediPhi-Clinical-GGUF)
- Others: [TheBloke on Hugging Face](https://huggingface.co/TheBloke)

**Quantization Recommendations**:

- `Q4_K_M` (2.5GB): **Fast, recommended** - Best balance for production
- `Q4_K_S` (2.3GB): **Fast, recommended** - Slightly smaller, good quality
- `Q8_0` (4.2GB): **Fast, best quality** - Higher accuracy
- `Q6_K` (3.2GB): **Very good quality** - Middle ground

## Next Steps

1. ✅ **Phase 1.5**: Local LLM provider (current)
2. **Phase 2**: OpenAI, AWS Bedrock, Azure providers
3. **Phase 3**: Streaming responses (SSE/WebSocket)
4. **Phase 4**: Fine-tuned medical models

---
**Status**: Implementation complete • Local LLM ready • Cloud providers planned

*2026-01-02 00:15:00*
