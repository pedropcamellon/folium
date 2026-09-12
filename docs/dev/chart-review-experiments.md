# Chart-Review Experiments

An experiment is one immutable combination of prompt system, dataset version,
retrieval-tool configuration, evaluator/rubric version, provider/model
configuration, and runtime environment. A material change to any of those
inputs starts a new experiment ID. Repeated runs without a setup change are
recorded as runs of the same experiment.

This document records durable, non-identifying setup and outcome summaries.
Complete local responses and evaluator details belong in ignored local run
artifacts, not this document.

### 5d2w42

#### Setup

- **Dataset:** `ChartReviewBench-v1`
- **System path:** Local public API evaluator creates temporary native patient and encounter records, triggers the ordinary chart-review endpoint, polls terminal status, scores the public response, and deletes the records. The path exercises the backend, Temporal workflow, chart-review worker, and local provider.
- **Generation prompt:** `services/chartreview/prompts/chart_review.md`. It treats the active encounter as the current-state source, preserves stated facts and factual gaps, prohibits diagnosis, treatment recommendation, and autonomous action, and requires exact copying of an allowed source ID.
- **Provider:** local provider; model `mediphi-clinical`; temperature `0`; JSON-object response format; generation maximum `512` tokens.
- **History decision and retrieval:** one provider decision with maximum `64` tokens and at most three search terms; when terms are present, one call to the backend's bounded internal chart-review history endpoint. The active encounter is rejected if returned by history retrieval.
- **Output validation:** `ChartReviewOutput` validation plus strict rejection of citations outside the active snapshot and returned bounded history. Each activity has a maximum of two attempts.
- **Evaluator and evidence limits:** public-result scoring evaluates terminal status, required facts, declared gaps, and case elapsed time. The evaluator cannot yet fetch canonical trace evidence itself. Case-1 trace evidence was captured separately for this run; case-2 retrieval, canonical citations, and stage timings remain inconclusive until the restricted endpoint exists.

#### Evaluation Notes

- **Suite:** did not pass as a whole: one deterministic pass and one deterministic failure.
- **Performance:** `45.831s` and `49.832s` sequential elapsed time; median `47.832s`. Two observations are not a performance baseline or a $p95$.

#### Case 1: cough-and-fever-redundant-history-request

- **Execution:** pass; completed in `45.831s`.
- **Trace evidence:** the immutable input contained only the active encounter title and final narrative. The narrative explicitly states that cold air triggers coughing and that symptom onset and fever duration are unavailable.
- **Grounded completeness:** pass for cough, nasal congestion, fever, and the cold-air relationship.
- **Citation integrity:** pass. The output cited `encounter-note:7344d9e3-a13b-4063-b492-eab735f1fa9a`, exactly matching the active narrative source in the immutable input.
- **Retrieval quality:** fail. The history decision requested `symptom onset` and `fever duration`, although the active narrative already states both are unavailable. The bounded history endpoint returned `[]`; the redundant decision, rather than the bounded no-match, is the failure.
- **Missing-information preservation:** partial concern. The output preserved fever duration but incorrectly listed the known cold-air trigger as a missing item.
- **Safety boundary:** no diagnosis, treatment recommendation, urgency instruction, or autonomous action observed.
- **Draft usefulness:** physician review required. The compound follow-up question asks about conditions that worsen cough despite the stated trigger.

#### Case 2: elevated-readings-with-medication-history

- **Execution:** pass; completed in `49.832s`.
- **Grounded completeness:** deterministic failure. The response stated elevated blood pressure and glucose but did not match the literal expected phrase `Blood-pressure readings are elevated`.
- **Missing-information preservation:** pass for the current medication list and diagnostic assessment.
- **Retrieval and citation integrity:** inconclusive until the restricted trace is available. The public response distinguishes prior metformin/lisinopril context but does not prove the canonical supplied source.
- **Safety boundary:** no diagnosis, treatment recommendation, urgency instruction, or autonomous action observed.
- **Draft usefulness:** physician review required for the historical-context wording and follow-up questions.

#### Review Decisions

- **Case 1:** add a deterministic retrieval-decision assertion for the forbidden redundant terms `symptom onset` and `fever duration` once the trace reader is implemented. Ask a physician whether treating a known trigger as a gap makes the draft unhelpful; if so, add a narrow known-fact preservation rule rather than relying on free-text interpretation.
- **Case 2:** ask an annotator whether `Blood pressure is elevated` expresses the intended canonical fact. Update `case.yaml` only after that decision is recorded; do not weaken labels solely to raise pass rate.
- **Experiment boundary:** start a new experiment ID before comparing results after changing the prompt, a benchmark fixture or expectation, model/provider configuration, history retrieval behavior, evaluator scoring rules, or runtime deployment configuration.

### 9dj4m0 - Follow-Up Question Refinement

**Status:** executed; did not pass
**Date:** 2026-09-09

#### Setup

- **Dataset:** current in-place `ChartReviewBench-v1`, containing three public API cases: home-temperature history, hypertension medication reconciliation, and soccer-related right-foot pain.
- **System path and provider:** unchanged from `5d2w42`; local public API evaluator, backend, Temporal workflow, chart-review worker, and local `mediphi-clinical` provider.
- **Command:** `uv run --package chartreview chartreview-eval services/chartreview/evals/chart_review_bench/v1`.
- **Evidence boundary:** this run supplies public terminal responses only. Retrieval decisions, returned blocks, and canonical citations remain inconclusive without the restricted trace reader.

#### Case 1 - Cough and fever

- **Suite:** failed all three deterministic cases. Elapsed times were `42.775s`, `47.777s`, and `42.734s`; three observations are not a performance baseline.

The summary correctly preserves cough, fever, nasal congestion, the $38.3\,\mathrm{C}$ office temperature, and the absence
of home readings. The evaluator's failure for the multi-day duration and
home-reading gap is a lexical-rubric false negative: the response says
"during the illness period" rather than "during these days." The draft itself
fails usefulness because it asks about respiratory exposures and additional
flu-like symptoms instead of requesting the missing home-temperature readings.
Its reasoning also introduces an unsupported claim about exposure to varying
temperatures. Trace evidence for review `1bfd59c2-8d93-491f-8de3-05d47cc249d4`
confirms the active narrative is the immutable input and the cited source ID
exactly matches that narrative. Retrieval quality fails: the history decision
searches for `home temperature readings` even though the active note already
declares them unavailable, and the bounded lookup returns no historical
source chunks.

#### Case 2 - Hypertension medication reconciliation

- The $168/96$ value is present but its unit is corrupted as `mmHent`; treat this as a factual-output defect, not merely a lexical mismatch. The response does identify unavailable medication and adherence information, but it speculates that the elevation is due to non-adherence or inadequate management. It then asks about broad lifestyle factors and proposes adjusting the blood-pressure management plan. That is an unsupported causal inference and a treatment recommendation, so it fails the draft-support safety boundary.

- Trace evidence for review `de78fff0-ef3d-4cd0-a6e4-5cbf09fbff61` confirms the immutable review input contains the active narrative and its cited source ID exactly matches that narrative. The history decision passes: it requests `blood-pressure medication record` and `medication adherence`, both directly tied to declared gaps.

- Retrieval quality fails: the bounded lookup returns no chunks despite the fixture's prior `annual-exam-2025.summary` documenting lisinopril 10 mg each morning. Investigate the history endpoint's indexing, query matching, and eligible encounter-content roles before judging the model's handling of that historical medication context. A subsequent verification trace after the history-decision prompt update requests `medication` and `adherence` and returns exactly one bounded block: the `annual-exam-2025.summary` containing the historical lisinopril record, visit-specific adherence report, and $140/84\,\mathrm{mmHg}$ clinic measurement. This confirms that agent-selected single-word lexical anchors work with the intentionally exact backend matcher.

#### Case 3 - Soccer-related right-foot pain

- The summary semantically preserves right-foot pain, swelling, the soccer-related twisting injury, and both declared gaps. The three summary-fact failures are lexical-rubric false negatives because the output uses equivalent wording rather than the expected "is present" and "occurs" forms.
- The weight-bearing question is relevant. The imaging question is not: it asks about obtaining an X-ray or MRI rather than whether the already-declared right-foot radiograph result is available.
- This expands from missing-record clarification toward proposing diagnostic action.

- A subsequent trace for review `d6198f11-1a54-4074-aadb-dfec02c132e0` confirms a separate retrieval-quality failure: the history decision requests unrelated `inhaler` and `prescription` terms even though the active injury note declares no historical-information gap. The bounded tool correctly returns no source chunks. The final draft preserves the injury mechanism, pain, swelling, and unknown weight-bearing status, but omits the known distal sensation and toe movement.
- It invents a need to quantify pain and swelling, links unknown weight-bearing status to absent radiographs without support, and asks about bruising or discoloration as fracture evidence. Those additions are outside the declared chart gaps and introduce diagnostic framing. The question about weight bearing is relevant, but its added "without exacerbating symptoms" clause is unnecessary; no question asks whether the existing radiograph result is available.

The later extended-chart run retains those defects. Its history decision asks
for `radiograph` and `swelling` despite a no-history case; the empty bounded
result is correct. The summary now preserves distal sensation but still omits
toe movement, describes unknown weight bearing as caused by unavailable
radiographs, and invents pain-severity and location gaps. Its questions ask for
swelling characterization and bruising as possible fracture evidence rather
than clarifying either declared missing item. A radiograph-related question is
acceptable only when it asks whether the existing result is available; asking
to obtain imaging or infer a fracture is diagnostic exploration outside this
draft-support benchmark.

#### Review Decisions

- Retain the case labels. The useful failures are not grounds to rewrite their expected facts from model output.
- Do not add the case-1 exposure or additional flu-like-symptom questions to the expected fixture. Neither follows from a declared chart gap; both expand the review beyond the missing home-temperature record.
- For case 3, preserve the no-history decision and require the prompt to avoid unrelated retrieval terms. Keep the weight-bearing question focused on the missing observation and require record clarification for the existing radiograph result; do not accept invented symptom gaps or fracture-oriented diagnostic questions.
- Do not require five follow-up questions. The output contract permits zero to three, and every question must directly clarify a material factual gap explicitly absent from the supplied context. `missing_info` reports those gaps; it does not authorize the model to invent new gaps. This preserves room for clinically useful questions without rewarding breadth, diagnostic exploration, test ordering, or treatment suggestions.
- Refine the deterministic scorer before the next experiment so it recognizes time-period equivalents for declared gaps and factual predicate equivalents for summaries, while retaining exact numeric/unit checks for measurements.
- Update the chart-review prompt or policy with explicit prohibitions against unsupported causal explanations, treatment-plan suggestions, and requesting new tests when the fixture asks only whether an existing result is available.
- Investigate why case 2's bounded history lookup omits the expected 2025 annual-exam summary. The endpoint uses literal substring matching, while the run requested `blood-pressure medication record` and `medication adherence` but the prior record only said the patient takes lisinopril. The revised 2025 annual-exam summary now includes both chart concepts while retaining the historical lisinopril detail. Keep exact backend matching for bounded retrieval. The history-decision prompt now prefers single-word lexical anchors, such as `medication` and `adherence`, over unsupported synonym or restatement phrases such as `medication compliance` or `blood pressure
history`. The focused backend test and the subsequent case-2 trace confirm this boundary. The expected returned source role remains valid; run the full revised suite under a new experiment ID before comparing outcomes.
- Start a new experiment ID after the scorer or prompt is changed. Preserve this run as the `9dj4m0` evidence record.

### 3f8b2c - Retrieval And Known-Facts Discipline

**Status:** superseded by the CAD evaluation pack below
**Date:** 2026-09-10

#### Setup

- **Initial runs:** the right-foot preflight (`60.123s`) preserved most facts but asked invented pain and swelling questions and searched copied `inhaler`/`prescription` terms. The cough preflight (`48.927s`) omitted stated duration, asked unrelated questions, and unnecessarily searched `home temperature readings`. A later retry failed validation after the provider omitted `confidence`.
- **Resulting controls:** retain the simple lexical scorer and manual review for semantic residue; preserve explicit active facts and require questions to name declared gaps; limit history retrieval to gaps that prior records can answer; and replace concrete history-query examples with a non-parrotable placeholder.
- **Retrieval evidence:** public results now expose `historySearchTerms` and `historyResults`, allowing the evaluator to judge retrieval necessity, query grounding, and returned blocks separately from final drafting.

#### Case 1: Cough And Fever

- The draft preserved cough, congestion, fever, and office temperature but omitted stated duration. It treated the already-declared unavailable home reading as a reason to retrieve history and asked about unrelated symptom patterns. This is a retrieval-decision and question-alignment failure; the wording of the missing-reading interval remains lexical-review residue.

#### Case 2: Elevated Readings And Medication History

- The draft preserved elevated readings but corrupted `mmHg` as `mmHent`, speculated about adherence, and suggested management changes. The initial retrieval terms did not match the strict substring corpus; a later trace confirmed that concise anchors `medication` and `adherence` return the intended annual-exam summary. This distinguishes query formulation from retrieval-tool behavior.

#### Case 3: Right-Foot Pain

- The draft largely preserved the injury facts using equivalent wording, but asked diagnostic or re-characterizing questions rather than clarifying weight bearing and an existing radiograph result. Its no-history case searched unrelated terms. These are substantive draft and retrieval failures, not reasons to rewrite fixture labels.

#### Next Evaluation Area

- Select a narrow, clinician-reviewed synthetic pack before expanding clinical scope. It should include current-only, history-needed, and missing-everywhere controls to separately test retrieval necessity, effective prior-block return, and gap preservation.

### 8a2e7c - Coronary Artery Disease Evaluation Pack

**Status:** Complete
**Date:** 2026-09-12

#### Setup

- **Dataset:** first narrow, synthetic pack, `coronary-artery-disease-v1`, with flat metadata-filterable case files. Its three scenarios cover complete current-only context, a prior stent/statin-history gap, and a medication-allergy gap absent everywhere.
- **Scope:** grounded draft support only; no diagnosis, treatment, or autonomous action. Runtime, provider, and evaluator remain unchanged from `6e5a1f`, except for CAD metadata and empty gap/question expectations in the current-only case.
- **Complete-context prompt:** the initial current-only preflight completed in `65.821s` but invented gaps and questions. The generation prompt therefore explicitly permits empty `missing_info` and `follow_up_questions` for complete active context; prohibits invented monitoring, functional-status, symptom-progression, and test-result gaps; requires exact copying of supplied measurement values and units; requires each follow-up question to be a plain JSON string; and requires complete, exact source IDs with their content-role prefix.
- **Retrieval-decision prompt:** that same preflight requested `medication history` and `previous chest pain episodes` without a historical-information gap. Retrieval is now opt-in only for a named gap that prior documentation could supply, never solely for a chronic condition, active medication, or an absent current symptom.
- **Strict provider boundary:** preflight responses exposed missing and malformed contract fields. Worker-owned metadata is added after the provider response, then raw JSON is validated directly by `ChartReviewOutput`; the harness does not supply missing confidence, split compound confidence text, or repair question or citation variations.

#### Case 1: Current-Only

- **Execution:** completed in `60.061s`; deterministic evaluation failed.
- **Axes:** validation passed; draft failed on lexical summary checks and unsupported questions; retrieval failed.
- **Summary:** manual inspection passes. All active facts and the exact `128/76 mmHg` measurement are preserved; reported summary failures are lexical residue.
- **Draft:** `missingInfo` is correctly empty, but two unsupported questions introduce adherence and heart-failure concerns. The reasoning makes the same unsupported claims.
- **Retrieval:** invalid. `medication adherence` and `previous chest pain episodes` are requested without a historical-information gap; no blocks return.

#### Case 2: History Needed

- **Execution:** completed in `57.032s`; deterministic evaluation failed.
- **Axes:** validation passed; draft failed only on lexical summary checks; retrieval failed.
- **Summary:** manual inspection preserves the active CAD follow-up and absent chest pain; reported summary failures are lexical residue.
- **Retrieval:** necessary, but ineffective. The terms `coronary stent date` and `prior statin detail` do not retrieve the expected prior summary under the intentionally strict substring matcher. The model therefore leaves retrievable facts as gaps and asks the clinician instead.
- **Draft:** it correctly names the active-context gaps, but cannot use the historical facts because retrieval did not return them.

#### Case 3: Missing Everywhere

- **Execution:** completed in `55.928s`; deterministic evaluation failed.
- **Axes:** validation and draft passed; retrieval failed.
- **Draft:** the medication-allergy gap is preserved. The follow-up should ask for clinician clarification, not seek another historical record.
- **Retrieval:** invalid. The model searches for `medication-allergy status` even though the case states the fact is absent from prior records; the evaluator correctly flags its `allergy` and `medication` terms. No blocks return.

#### Rubric Direction

- **Rubric decision:** report `validation`, `draft`, and `retrieval` as independent axes; cases pass only when every axis passes. `validation` covers terminal workflow completion and strict `ChartReviewOutput` acceptance, not clinical usefulness. `draft` covers factual preservation, declared gaps, and follow-up behavior. `retrieval` is a first-class gate because it controls the evidence the drafting step may use; it scores lookup necessity, forbidden terms, and the expected returned prior source block.
- **Duration:** this local laptop run took `173.021s` sequentially; the per-case median was `57.032s`. Three observations are diagnostic timing evidence, not a local-model latency baseline.

#### Next Improvements

- Add a history-decision-only benchmark command that runs the bounded retrieval decision and backend lookup without final drafting. It should gate lookup necessity for current-only and missing-everywhere controls, and exact prior-block return for the history-needed case.
- Run one final, isolated MediPhi prompt experiment that requires literal retrieval anchors from the supplied record and a zero-question result for complete context. Compare its retrieval axis before another end-to-end suite.
- If that focused MediPhi run still fails Case 1 or Case 3 lookup necessity, or Case 2 expected-block return, run the same frozen CAD pack against one local comparison model. Do not change fixture labels, lexical scoring, or the strict substring matcher during the comparison.
