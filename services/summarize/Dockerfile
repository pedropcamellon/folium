# Clinical summarization service using the root uv workspace.
ARG PROVIDER=local

FROM ghcr.io/astral-sh/uv:python3.13-bookworm-slim AS base

ARG PROVIDER

WORKDIR /workspace

ENV PATH="/workspace/.venv/bin:$PATH" \
    CMAKE_ARGS="-DGGML_NATIVE=OFF -DGGML_CPU_ALL_VARIANTS=OFF"

# Install system dependencies
RUN apt-get update && apt-get install -y \
    build-essential \
    curl \
    && rm -rf /var/lib/apt/lists/*

COPY . .
RUN uv sync --frozen --no-dev --package summarize --extra "${PROVIDER}"

# Local models are mounted at runtime from ./services/summarize/models.
RUN mkdir -p /models

WORKDIR /workspace/services/summarize

# Expose service port
EXPOSE 8002

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=60s --retries=3 \
    CMD curl -f http://localhost:8002/health || exit 1

# Run the application with auto-reload for development
CMD ["uv", "run", "--frozen", "--no-sync", "--package", "summarize", "uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8002", "--reload"]

