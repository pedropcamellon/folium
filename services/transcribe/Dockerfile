# Transcription service using the root uv workspace.
ARG PROVIDER=whisper

FROM ghcr.io/astral-sh/uv:python3.13-bookworm-slim AS base

ARG PROVIDER

WORKDIR /workspace

ENV PATH="/workspace/.venv/bin:$PATH"

# Install system dependencies
RUN apt-get update && apt-get install -y \
    ffmpeg \
    wget \
    && rm -rf /var/lib/apt/lists/*

COPY . .
RUN uv sync --frozen --no-dev --package transcribe --extra "${PROVIDER}"

# Pre-download Whisper model to cache it in the image
ENV HF_HOME=/workspace/services/transcribe/.cache/huggingface
RUN if [ "$PROVIDER" = "whisper" ]; then \
        python -c "from faster_whisper import WhisperModel; WhisperModel('base', device='cpu', compute_type='int8')"; \
    fi

WORKDIR /workspace/services/transcribe

# Expose port
EXPOSE 8001

# Health check using wget (lightweight)
HEALTHCHECK --interval=30s --timeout=10s --start-period=40s --retries=3 \
    CMD wget --no-verbose --tries=1 --spider http://localhost:8001/health || exit 1

# Run application
CMD ["uv", "run", "--frozen", "--no-sync", "--package", "transcribe", "uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8001"]
