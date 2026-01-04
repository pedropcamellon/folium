# Multi-stage Dockerfile for clinical summarization service
# Supports multiple providers: local (default), openai, bedrock, azure

# Build argument to select provider (default: local)
ARG PROVIDER=local

# ============================================================================
# Base Stage: Common dependencies for all providers
# ============================================================================
FROM python:3.11-slim AS base

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    build-essential \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Install uv for fast dependency management
RUN pip install --no-cache-dir uv

# Copy dependency files and source code
COPY pyproject.toml README.md ./
COPY app ./app
COPY prompts ./prompts

# ============================================================================
# Local LLM Stage: Install llama-cpp-python
# ============================================================================
FROM base AS provider-local

# Install llama-cpp-python (CPU-only)
RUN uv pip install --system llama-cpp-python

# Install base dependencies
RUN uv pip install --system .

# Copy MediPhi-Clinical model (from local cache or download manually)
# If models/model.gguf exists locally, it will be copied. Otherwise:
# Download manually: curl -L https://huggingface.co/mradermacher/MediPhi-Clinical-GGUF/resolve/main/MediPhi-Clinical.Q4_K_S.gguf -o models/model.gguf
RUN mkdir -p /models
COPY models/model.gguf /models/model.gguf

# ============================================================================
# OpenAI Stage: Install OpenAI SDK
# ============================================================================
FROM base AS provider-openai

# Install dependencies with openai extras from pyproject.toml
RUN uv pip install --system --no-cache ".[openai]"

# ============================================================================
# AWS Bedrock Stage: Install boto3
# ============================================================================
FROM base AS provider-bedrock

# Install dependencies with aws extras from pyproject.toml
RUN uv pip install --system --no-cache ".[aws]"

# ============================================================================
# Azure OpenAI Stage: Install Azure SDK
# ============================================================================
FROM base AS provider-azure

# Install dependencies with azure extras from pyproject.toml
RUN uv pip install --system --no-cache ".[azure]"

# ============================================================================
# Final Stage: Select provider and copy application code
# ============================================================================
FROM provider-${PROVIDER} AS final

WORKDIR /app

# Expose service port
EXPOSE 8002

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=60s --retries=3 \
    CMD curl -f http://localhost:8002/health || exit 1

# Run the application with auto-reload for development
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8002", "--reload"]

