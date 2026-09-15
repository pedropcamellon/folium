# User guide

Folium's user-facing workflow is a synthetic, clinician-reviewable demonstration
of bounded draft support. It is not a complete EHR and is not a production
clinical system.

## Supported lane

The current lane is:

1. Start with an approved synthetic patient and interaction context.
2. Capture or review interaction notes and available voice-note transcripts.
3. Ask for a chart-review draft from a selected interaction.
4. Inspect structured validation results, citations, confidence, and review flags.
5. A clinician reviews the draft and makes every clinical decision.

The system does not diagnose, recommend treatment, use real patient data, or take
autonomous action.

## Guides

- [Synthetic patients and interactions](patients-and-interactions.md)
- [Voice-note processing](voice-notes.md)
- [Chart-review drafts](chart-review.md)
- [Lifecycle, citations, and review flags](lifecycle-citations-and-flags.md)

## Planned behavior

Broader document retrieval, confidence calibration, dedicated local serving
performance, cloud providers, and cloud deployment are planned work. They are
not supported user workflows today.
