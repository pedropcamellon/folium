FROM ghcr.io/astral-sh/uv:python3.13-bookworm-slim

ENV PYTHONDONTWRITEBYTECODE=1 PYTHONUNBUFFERED=1 PATH="/workspace/.venv/bin:$PATH"
WORKDIR /workspace
COPY . .
RUN uv sync --frozen --no-dev --package chartreview
WORKDIR /workspace/services/chartreview
CMD ["uv", "run", "--frozen", "--no-sync", "--package", "chartreview", "python", "-m", "app.worker"]