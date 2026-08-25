# feat-chart-review-agent — Synthetic Chart Review Agent

- **GitHub Issue:** [#20](https://github.com/pedropcamellon/folium/issues/20)
- **Labels:** `spec`, `area:backend`, `area:temporal`
- **Milestone:** Agentic Eval Platform
- **Status:** Spec
- **Priority:** P0
- **Estimate:** L

## Description

A bounded clinical draft-support agent that collects patient context (timeline,
documents, interaction notes, voice note transcript) and produces a structured
output: patient summary, missing information flags, suggested follow-up questions,
source references, and a confidence score.

Framed explicitly as **draft support**, not clinical decision-making. All data is
synthetic — no real patient records required at any point.

This is the flagship agentic feature: it drives the eval runner, the Temporal
orchestration story, and the observability layer.

## Acceptance Criteria

- [ ] Agent accepts a patient context bundle (timeline, docs, interactions, optional transcript); all fields populated from synthetic fixtures.
- [ ] Output is a validated Pydantic model: `summary`, `missing_info[]`, `follow_up_questions[]`, `source_refs[]`, `confidence` (0–1), `review_flags[]`.
- [ ] Structured output validation failure is an explicit error state, not a silent partial result.
- [ ] Agent is provider-pattern pluggable (swap LLM without changing orchestration).
- [ ] A mock agent provider returns deterministic output for CI and local dev (no live LLM call required).
- [ ] Output is persisted and linked to the source patient + interaction record.
- [ ] All input data can be synthetic; no real patient data required.

## Dependencies

- `feat-patients-crud`, `feat-interactions`, `feat-voice-notes` (source records must exist).
- `feat-eval-temporal-activity` (Temporal WF wraps this agent).

## Notes

- Frame as "draft support" in UI copy and code comments — not diagnosis, not recommendation.
- Source refs must be traceable to actual input chunks; do not hallucinate citations.
- Confidence below threshold should set `review_flags` automatically.
- Start with a single-call agent; agentic loop / tool-calling is a v2 extension.

## Validation Plan

```bash
cd backend && uv run pytest -k chart_review
# Smoke: inject synthetic patient bundle, assert output schema validates
# Edge: malformed input → validation error, not 500
```

--- DEV / CODING AGENT ZONE ---

## Checklist

### 1. Establish the Domain Contract

- [ ] Inspect the existing patient, interaction, document, and voice-note models to identify stable source identifiers and fields available to the agent.
- [ ] Define `ChartReviewInput` with validated synthetic context for timeline entries, documents, interactions, and an optional transcript.
- [ ] Define `ChartReviewOutput` with `summary`, `missing_info`, `follow_up_questions`, `source_refs`, `confidence`, and `review_flags`.
- [ ] Define structured validation errors for malformed provider output; do not permit partial output.
- [ ] Add unit tests for valid input/output contracts, confidence bounds, and invalid structured output.

### 2. Build the Provider Boundary

- [ ] Define a provider protocol that accepts `ChartReviewInput` and returns `ChartReviewOutput`.
- [ ] Implement a deterministic mock provider that emits source references drawn only from supplied input chunks.
- [ ] Add service-level tests proving the mock requires no live model credentials or network access.
- [ ] Add configuration for selecting the mock provider by default and a real provider only when explicitly enabled.

### 3. Implement the Review Service

- [ ] Implement `ChartReviewService` to collect and normalize the source context into `ChartReviewInput`.
- [ ] Invoke the configured provider and surface output-validation failures as an explicit service error state.
- [ ] Apply the review-flag policy when confidence is below the configured threshold.
- [ ] Test successful review generation, malformed provider output, missing source records, and low-confidence output.

### 4. Persist and Expose Results

- [ ] Add a persistence model and repository for chart-review outputs linked to the patient and originating interaction.
- [ ] Persist the validated output and its traceable source references atomically.
- [ ] Add a read path or API response model needed by the calling workflow/UI, preserving the draft-support framing.
- [ ] Test persistence linkage and source-reference integrity using synthetic fixtures.

### 5. Integrate the Workflow and Real Provider

- [ ] Add a Temporal activity boundary that calls the chart-review service and propagates explicit validation failures.
- [ ] Implement the Azure or Bedrock provider behind the existing provider-selection configuration.
- [ ] Verify provider responses are validated through the same output contract as the mock.
- [ ] Run the focused chart-review test suite and a workflow smoke test with synthetic data.

## Implementation Notes

-

## Changed Files

-

## Blockers

-

## Next Action

- [ ] Inspect the existing source-record models, then define the Pydantic input/output contract and its focused tests.
