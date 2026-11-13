# Folium Runtime

Developer tooling for the documented Folium local runtime.

Run from the repository root with `uv run folium` or directly with
`uv run --package folium_runtime folium`.

The default local selection includes MLflow at `http://localhost:5000` for
chart-review evaluation tracking.

## Optional X-ray review

Run `uv run folium` and select **X-ray review (research only)** with Space.
It is unselected by default. Use `b` to build or `x` to recreate it; its logs
are included when selected alongside the frontend/backend. Selecting the service
explicitly starts it even though it belongs to the `xray-review` Compose profile.

Set a private, nonempty `XRAY_REVIEW_SERVICE_TOKEN` in root `.env` before
starting. Recreate Backend API if that value changed after it started. The
imaging service downloads and verifies the pinned model on first startup;
wait for container health before submitting a scan. The model is research-only,
not a diagnostic or nodule-localization tool.
