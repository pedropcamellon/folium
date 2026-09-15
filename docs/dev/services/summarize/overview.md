# Summarization service

Folium keeps summarization in a focused service because it has different
runtime needs from interactive clinical workflows. Model initialization,
processing time, and compute capacity can change independently without making
the backend or frontend responsible for provider behavior.

## Service boundary

The service accepts approved transcript input and returns structured output
through a typed contract. It owns provider configuration and prompt behavior;
the backend retains workflow policy, data access, validation, and review
routing. This prevents a provider SDK or model choice from spreading through
the rest of the platform.

## Provider boundary

The service selects one configured provider for a running instance and keeps
provider initialization and configuration behind its service contract. This
allows the application to change a provider without changing the backend's
workflow code or the frontend's integration. A provider is useful only when it
can produce the validated result expected by the platform.

## Structured results

Summarization output is structured so downstream workflows can validate it and
present it consistently for review. The service is designed to preserve the
source transcript's meaning without turning generated content into an
unreviewed clinical decision. Prompt and model changes therefore belong with
the service and require evaluation evidence before they are treated as reliable.

## Local first, hosted later

The local provider path supports on-prem operation without requiring cloud
credentials. Azure and AWS provider paths remain planned. Enabling either is a
deployment decision that requires explicit identity, network, data-residency,
cost, and validation work, not a change to the calling workflow.

**Technology**: llama-cpp-python with GGUF quantized models

**Recommended Model: MediPhi-Clinical (3.8B)**

- Fine-tuned from Phi-3.5-mini-instruct for clinical NLP
- Trained on PubMed, clinical notes, medical guidelines, ICD coding
- MIT licensed, HIPAA-compliant (no BAA required)
- 128k context window (handles long clinical documents)
- Outperforms GPT-4 on ICD-10 coding by 14% (68.7% vs 54.7%)
- Q4_K_M quantization: 2.5GB (fast, recommended)
- Q4_K_S quantization: 2.3GB (fast, recommended, slightly smaller)
- Q8_0 quantization: 4.2GB (fast, best quality)

**Alternative Models**:

- Llama 3.1 8B Instruct (Q4_K_M, ~5GB, general purpose)
- Mistral 7B Instruct (Q4_K_M, ~4GB, general purpose)
- Phi-3 Mini (Q4_K_M, ~2GB, fast but less accurate)

**Configuration**:

- Context window: 4096-8192 tokens (MediPhi supports 128k)
- Temperature: 0.3 (low creativity, high consistency)
- Max tokens: 500 (summary length limit)
- CPU threads: Auto-detect (optimize for multi-core)

**Performance (MediPhi-Clinical Q4_K_M)**:

- Processing time: ~5-10 seconds (50-200 word transcript)
- CPU usage: 60-80% during generation
- Memory: 4-5GB (model + context)
- Model size: 2.5GB on disk
- Clinical accuracy: Excellent (95%+ on CLUE+ benchmark)
- ICD-10 coding: 68.7% accuracy (beats GPT-4 by 14%)

**No External Dependencies**: Runs entirely offline. No API keys, no network calls. HIPAA compliant by default.

**Limitations**:

- CPU-bound (GPU support requires CUDA)
- Context window smaller than cloud providers on alternative models
- May hallucinate if transcript ambiguous (mitigate with strict prompts)

## Technical Decisions & Rationale

### Structured Output Format

**Implementation**: Force JSON output via prompt engineering or native JSON mode (OpenAI/Azure).

**Benefits**:

- Consistent parsing (no regex hacks)
- Type-safe backend integration
- Enables downstream processing (ICD coding, action items)

**Format**: SOAP-like structure with clinical tags, ICD codes, action items.

### Async Background Task

**Same pattern as transcription service**: Upload/trigger → Background task → Poll for updates

**Benefits**:

- Non-blocking API (immediate response)
- Consistent UX across transcription + summarization
- Simple frontend polling (no WebSocket complexity)

## Integration with Transcription Service

**Workflow**: Transcription → Summarization (chained microservices)

**Flow**:

1. User records voice note → Transcription service generates transcript
2. Backend detects transcript completion → Triggers summarization
3. Summarization service processes transcript → Returns structured summary
4. Backend updates interaction with both transcript and summary
5. Frontend displays both in interaction detail modal

**Data Flow**:

```
Audio → [Transcribe Service] → Transcript
       ↓
Transcript → [Summarize Service] → Structured Summary
```

**Benefits of Separation**:

- Independent scaling (transcription vs summarization workloads)
- Different provider strategies (Whisper for audio, Llama for text)
- Reusable (summarize existing notes, not just new transcripts)

See [planned Azure provider](azure-provider.md) and
[planned AWS provider](aws-provider.md) for those deployment directions.
