FROM ghcr.io/astral-sh/uv:python3.13-bookworm-slim AS base

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PATH="/workspace/.venv/bin:$PATH"

WORKDIR /workspace

COPY . .

RUN uv sync --frozen --no-dev --package voicenotes

WORKDIR /workspace/services/voicenotes
CMD ["uv", "run", "--frozen", "--no-sync", "--package", "voicenotes", "python", "-m", "app.worker"]