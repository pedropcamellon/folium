# Architecture overview

Folium is an on-prem-first platform for modern, reviewable clinical-record
workflows. It is designed to make secure clinical operations easier to build,
run, and review. Folium is not a complete EHR.

## What runs here

- The Next.js frontend provides clear, task-focused review surfaces.
- The FastAPI backend owns data access, validation, and workflow initiation.
- Focused transcription and summarization services process approved typed input.
- `folium-core` provides stable shared contracts and pure runtime primitives.
- MLflow and Temporal record evaluation evidence and workflow audit context.

Security and data-boundary decisions are owned by the platform, while human
review remains part of supported workflow design. Synthetic fixtures support
safe local development and evaluation; they do not define the product. Feature
workflows and their clinical boundaries are documented in the user and
developer guides that own them.

Next: [service boundaries](service-boundaries.md) and
[deployment modes](deployment-modes.md).
