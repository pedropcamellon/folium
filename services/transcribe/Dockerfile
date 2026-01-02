# Multi-stage Dockerfile for provider selection
# Build with: docker build --build-arg PROVIDER=whisper -t transcribe:whisper .

ARG PROVIDER=whisper

# ============== Base Stage ==============
FROM python:3.11-slim as base

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    ffmpeg \
    wget \
    && rm -rf /var/lib/apt/lists/*

# Copy dependency files
COPY pyproject.toml ./

# Install uv for fast dependency management
RUN pip install --no-cache-dir uv


# ============== Whisper Stage (HIPAA - Self-hosted) ==============
FROM base as whisper

RUN uv pip install --system -e .[whisper]

# Pre-download Whisper model to cache it in the image
ENV HF_HOME=/app/.cache/huggingface
RUN python3 -c "from faster_whisper import WhisperModel; WhisperModel('base', device='cpu', compute_type='int8')" && \
    echo "✅ Whisper base model cached in image"


# ============== AWS Stage (Requires BAA) ==============
FROM base as aws

RUN uv pip install --system -e .[aws]


# ============== Azure Stage (Requires BAA) ==============
FROM base as azure

RUN uv pip install --system -e .[azure]


# ============== Final Stage ==============
FROM ${PROVIDER} as final

WORKDIR /app

# Copy application code
COPY app/ ./app/

# Copy cached models from build stage (for Whisper)
ENV HF_HOME=/app/.cache/huggingface

# Expose port
EXPOSE 8001

# Health check using wget (lightweight)
HEALTHCHECK --interval=30s --timeout=10s --start-period=40s --retries=3 \
    CMD wget --no-verbose --tries=1 --spider http://localhost:8001/health || exit 1

# Run application
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8001"]
