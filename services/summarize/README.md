# Clinical Summarization Service

FastAPI microservice for generating structured clinical summaries from transcripts. Supports local LLMs and cloud AI providers (AWS Bedrock, Azure OpenAI, OpenAI).

## Quick Start

### Docker Compose

1. Download a GGUF model file (MediPhi-Clinical recommended) or configure cloud provider credentials
2. Run `docker compose up`
3. Test endpoint: `POST http://localhost:8002/summarize`

### Local Development

Install dependencies with `uv pip install -e .`, configure provider via environment variables, and run `uvicorn app.main:app --reload --port 8002`

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

## API Endpoints

- `POST /summarize` - Generate structured SOAP note from clinical transcript
- `GET /health` - Health check

See SPEC.md for detailed request/response schemas.                 ┌──────────────────┐
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
FastAPI service with abstract provider pattern. Providers implement `SummarizationProvider` interface. Factory selects provider based on environment configuration. See SPEC.md for architecture diagrams and details
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

