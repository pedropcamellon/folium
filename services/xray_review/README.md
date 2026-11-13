# X-ray review reference app

This is a separately deployable reference integration, not a runtime plugin. Folium calls
its versioned `POST /v1/analyze` endpoint from the backend. Run it on a trusted private
network; do not expose the service publicly. The endpoint receives the image but no patient
identifier, and the app does not persist the image or log its contents.

The app downloads the MIT-licensed `itsomk/chexpert-densenet121` checkpoint at pinned
revision `81be45e4d43011e8f50e17d002190c76cb069edd` on startup, verifies its SHA-256 and
byte size, then loads the weights locally. The model card describes the model as research
and educational use only and explicitly says it is not for clinical use. The CheXpert
classifier returns 14 labels, including `Lung Lesion`; it does not detect or localize
nodules. Scores are not calibrated probabilities. This reference app is for synthetic
demonstrations and offline evaluation, not patient care.

To run locally, install the project dependencies and start `uvicorn app.main:app` from this
directory on port 8010. Set `XRAY_REVIEW_TOKEN` on the service and the matching
`XRAY_REVIEW_SERVICE_TOKEN` in Folium's backend using a secret manager. Configure
`XRAY_REVIEW_SERVICE_URL` to reach the service. Model weights are cached outside the
repository by Hugging Face Hub and are not committed.

The Folium-side job record currently uses FastAPI background tasks. It provides visible
pending/processing/complete/failed states, but is not a durable queue; deploy a durable
worker before production use.
