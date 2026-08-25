# Backend Dockerfile - FastAPI with uv for fast dependency management
FROM ghcr.io/astral-sh/uv:python3.13-bookworm-slim AS base

WORKDIR /workspace

ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PATH="/workspace/.venv/bin:$PATH"

# Development stage
FROM base AS development

COPY . .
RUN uv sync --frozen --package folium --extra dev --group dev

# Expose port
EXPOSE 8000

WORKDIR /workspace/backend
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000", "--reload"]

# Production stage
FROM base AS production

COPY . .
RUN uv sync --frozen --no-dev --package folium

# Create non-root user
RUN useradd -m -u 1000 appuser && chown -R appuser:appuser /workspace
USER appuser

# Expose port
EXPOSE 8000

WORKDIR /workspace/backend
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
