FROM python:3.13-slim

WORKDIR /app
ENV HF_HOME=/tmp/huggingface
COPY pyproject.toml .
COPY app ./app
RUN mkdir -p /tmp/huggingface && chown -R 10001:0 /tmp/huggingface \
    && pip install --no-cache-dir .
USER 10001
EXPOSE 8010
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8010"]
