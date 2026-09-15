# Synthetic patients and interactions

Folium's current examples use synthetic patients and local development data.
They exist to exercise the workflow and must not be replaced with real patient
data.

## Review a patient context

1. Start the local stack and open the frontend.
2. Select a seeded synthetic patient.
3. Open an interaction from the patient's history.
4. Review the interaction note, transcript, and available source context.

The patient history is a view over typed records. An interaction is a bounded
clinical contact with its own notes and workflow state; it is not a diagnosis,
treatment plan, or unrestricted chart search.

## Capture interaction context

An interaction can contain manually entered narrative and, where enabled, a
voice-note recording and transcript. Review and correct captured text before
requesting draft support. The current chart-review request uses the selected
interaction as its immutable starting context.

## Review generated support

Use the chart-review action only when a clinician wants draft support for the
selected interaction. Processing, completion, failure, source citations, and
review flags are described in the [chart-review guide](chart-review.md).

## Boundaries

- Synthetic local data only.
- No diagnosis or treatment recommendation.
- No automatic updates to the patient record.
- No autonomous action or follow-up.
- No unrestricted retrieval of documents or the full chart.
