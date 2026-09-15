# Voice-note processing

Voice notes are available as interaction capture material in the local synthetic
workflow. They are not an autonomous clinical service and they do not replace
review of the original audio or transcript.

## Capture a note

1. Open a seeded synthetic patient.
2. Create or open an interaction.
3. Start a voice-note recording when the local frontend offers the control.
4. Stop the recording and wait for processing.
5. Review and correct the transcript in the interaction before using it as draft
   context.

Browser microphone permission and a running local voice-note service are
required. Exact processing time depends on the local environment; no fixed
latency or accuracy guarantee is part of the current contract.

## Review a transcript

Treat transcription as a draft capture. Compare it with the recording, correct
names and clinical terms, and do not infer missing content. A corrected
transcript remains interaction context and requires human review.

## Use with chart review

A clinician may select the interaction and request a bounded chart-review draft
after reviewing the available transcript. The draft uses approved interaction
context and exposes citations, validation findings, confidence attributes, and
review flags.

## Current boundaries

- Use synthetic local data only.
- The service does not diagnose or recommend treatment.
- The service does not make clinical decisions or take autonomous action.
- Broader document retrieval and cloud transcription providers are planned, not
  supported workflows.
