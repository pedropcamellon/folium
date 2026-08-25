# Voice Note Workflow Service

Dedicated Temporal worker service for Folium voice note processing.

This service owns workflow orchestration only. The backend API remains responsible for request validation, audio upload, initial interaction metadata persistence, and starting the workflow.

## Responsibilities

- Run the Temporal worker for the voice note domain
- Call transcription and summarization as external HTTP APIs
- Persist partial and final workflow status back to the backend API
- Keep orchestration logic isolated from the FastAPI runtime

## Scope

The minimal implementation assumes the backend uploads audio first and starts the workflow with a stable audio reference. For the first slice, the workflow input can also include an internal `audioUrl` until storage-signing is extracted into a shared adapter.

## Run

From the repo root:

```bash
docker compose up voice-note-worker temporal temporal-ui postgres transcribe summarize backend -d
```

## Design notes

- Transcription and summarization are treated as swappable external APIs
- The worker uses typed contracts so provider changes do not change workflow structure
- The backend API is the system of record for interaction state
