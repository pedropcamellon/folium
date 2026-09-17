from __future__ import annotations

import os
from urllib.parse import urlparse

BASE_URL = os.getenv("FOLIUM_BASE_URL", "http://localhost:3000")
API_BASE_URL = os.getenv("FOLIUM_API_BASE_URL", "http://localhost:8000").rstrip("/")
MINIO_ENDPOINT = os.getenv("FOLIUM_MINIO_ENDPOINT", "http://localhost:9000")
MINIO_BUCKET = os.getenv(
    "FOLIUM_MINIO_BUCKET", os.getenv("STORAGE_BUCKET", "folium-dev")
)
MINIO_ACCESS_KEY = os.getenv("FOLIUM_MINIO_ACCESS_KEY", "")
MINIO_SECRET_KEY = os.getenv("FOLIUM_MINIO_SECRET_KEY", "")
HEADLESS = os.getenv("PLAYWRIGHT_HEADLESS", "false").lower() == "true"
SLOW_MO_MS = int(os.getenv("PLAYWRIGHT_SLOW_MO_MS", "250"))
PROVIDER_WAIT_MS = int(os.getenv("FOLIUM_PROVIDER_WAIT_MS", "3000"))
FAKE_TRANSCRIPT = os.getenv(
    "FOLIUM_FAKE_TRANSCRIPT",
    "Patient reports improved sleep, mild residual cough, and no fever for the last 48 hours.",
)
CHROMIUM_LAUNCH_ARGS = [
    "--use-fake-ui-for-media-stream",
    "--use-fake-device-for-media-stream",
    "--mute-audio",
]


def _is_local_base_url(url: str) -> bool:
    hostname = urlparse(url).hostname
    return hostname in {"localhost", "127.0.0.1", "0.0.0.0"}


SUMMARY_WAIT_MS = int(
    os.getenv(
        "FOLIUM_SUMMARY_WAIT_MS",
        "120000" if _is_local_base_url(BASE_URL) else "15000",
    )
)
CHART_REVIEW_WAIT_MS = int(
    os.getenv(
        "FOLIUM_CHART_REVIEW_WAIT_MS",
        "660000" if _is_local_base_url(BASE_URL) else "30000",
    )
)
