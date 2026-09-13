# ChartReviewBench-v1

Committed anonymized chart-review benchmark cases. Each `patient-###`
directory is one case and contains a `case.yaml` seed plan.

`case.yaml` contains a short stable `id`, clinician-readable `title`,
non-identifying patient attributes, chronological encounters, one active
encounter, and deterministic output, history, and validation assertions. The
fixture loader validates the plan without touching persistence. A future
staging adapter will create isolated records from the same plan and execute the
workflow.

Each case's required `metadata` supports filtering:

```yaml
metadata:
  evaluation_pack: coronary-artery-disease-v1
  clinical_area: cardiovascular
  condition: coronary-artery-disease
  scenario: current-only
```

Run the fast fixture-and-pipeline integration test:

```bash
cd services/chartreview
uv run pytest tests/test_evals.py
```

Run the complete local suite. The evaluator reads only the explicit
`FOLIUM_EVAL_*` keys from the process environment or repository `.env`; it does
not load other `.env` values:

```bash
cd ../..
uv run --package chartreview chartreview-eval \
  services/chartreview/evals/chart_review_bench/v1
```

Pass an individual `patient-###/case.yaml` to run one case. Set
`FOLIUM_EVAL_ACCESS_TOKEN`, or both `FOLIUM_EVAL_USER_EMAIL` and
`FOLIUM_EVAL_USER_PASSWORD`, before running. The runner defaults to
`http://localhost:8000`; override it with `FOLIUM_EVAL_API_BASE_URL`. It creates
an isolated temporary patient and native encounters through public APIs, creates
the active final narrative, starts chart review, polls its terminal status,
scores the public result, and deletes the temporary patient. It exercises
backend routing, Temporal, the chart-review worker, and the local model service.
The terminal-review timeout defaults to 600 seconds; set
`FOLIUM_EVAL_POLL_TIMEOUT_SECONDS` for a different limit.
It writes ignored local manual-review artifacts to
`artifacts/evaluations/chart-review/<run-id>/`; set
`FOLIUM_EVAL_ARTIFACTS_DIR` to use another root. It also logs aggregate axis
and timing metrics, version tags, the compact review queue, and a safe summary
to the `chart-review-evaluations-v1` MLflow experiment at `http://localhost:5000`
by default. Start the local runtime first
with `uv run folium`. Raw review responses remain only in the ignored local
`suite.json` and `cases.jsonl` artifacts.

In MLflow, open `chart-review-evaluations-v1`, select a run, then open the
Metrics tab. Whole-case durations are `elapsed_seconds_min`,
`elapsed_seconds_median`, `elapsed_seconds_p95`, and `elapsed_seconds_max`.
Evaluator lifecycle durations are `<stage>_seconds_median` and
`<stage>_seconds_p95` for `seeding`, `review`, `evidence`, and `scoring`. The
evaluator records these client-observed durations; it does not yet record
provider-internal graph stage durations.

Set `FOLIUM_EVAL_INTERNAL_TOKEN` and `FOLIUM_EVAL_EVALUATION_TOKEN` to enable
the restricted terminal evaluation-evidence request. The backend requires both
the configured `CHARTREVIEW_INTERNAL_TOKEN` and `CHARTREVIEW_EVALUATION_TOKEN`.
It returns canonical source IDs only for evaluator-created synthetic reviews;
the user-facing chart-review API does not expose them.

Set `MLFLOW_TRACKING_URI` to choose another tracking backend. Chart-review
prompts are a committed registry: the current baseline is
`prompts/chart_review_v1.md`, selected by `CHARTREVIEW_PROMPT_VERSION=v1` in
the worker. The evaluator defaults to the same `v1` selection and records
`v1:sha256:<12-hex>` from that exact file. Set
`FOLIUM_EVAL_MODEL_NAME`, `FOLIUM_EVAL_DATASET_VERSION`, and
`FOLIUM_EVAL_RUN_LABEL` to label a frozen comparison explicitly. When adding a
new prompt candidate, add it to the registry, select it in both
`CHARTREVIEW_PROMPT_VERSION` and `FOLIUM_EVAL_PROMPT_VERSION`, restart the
worker, then run the unchanged suite. The runner otherwise uses the configured
`AI_MODEL_NAME` and derives the dataset version from the fixture pack metadata.

## Case Boundary

A case contains two separate concerns:

- `fixture` holds non-identifying patient attributes, chronological native
  encounters, and exactly one active encounter. The backend derives the
  immutable `ChartReviewInput`; fixture YAML never supplies a model prompt or
  agent input snapshot.
- `expected` holds observable output, bounded-history, and validation
  assertions. It is never supplied to the model.

The case schema is intentionally chart-review-specific. Shared dataset or
tracking abstractions remain deferred until a second service has a proven
compatible need.

## Expected Assertions

`expected.output` uses atomic assertions instead of a complete expected output
sentence-for-sentence:

- `summary_facts`: facts the summary must communicate.
- `missing_information`: factual gaps that must remain visible and must not be
  invented away.
- `forbidden_claims`: fixture-approved claim patterns that must not appear in
  the draft. This deterministic check is a floor for specific known risks, not
  a substitute for clinician review of clinical usefulness or safety.
- `required_follow_up_terms`: terms that the focused follow-up questions must
  communicate for a declared decision-relevant gap.
- `forbidden_follow_up_terms`: terms that would reopen a known fact or add
  unsupported speculation to a follow-up question.
- `required_source_roles`: fixture roles required by the future restricted
  canonical-provenance scorer, such as `active.note`.
- `forbidden_source_roles`: known invalid fixture roles, including an
  unsupplied content-role variant from the same encounter.
- `confidence`: optional until the confidence rubric is defined by task #40.

`expected.history_decision` declares whether a bounded lookup is expected and
the fixture roles expected to be returned. A no-retrieval or no-match result is
valid when active context already has the relevant fact or no approved history
block matches a genuine gap. Exact history and citation scoring remains deferred
until the restricted evaluation trace is implemented.

## Evaluation Axes

Each completed case has independently reported axes. A case passes only when
all applicable axes pass:

- `validation`: compares the terminal review status with
  `expected.validation.expected_status`. `valid` expects `completed`; `invalid`
  expects `failed`. It does not repair an invalid provider response.
- `draft`: checks required facts, preserved gaps, and bounded follow-up terms.
- `retrieval`: checks whether history was requested or returned as expected.
- `provenance`: resolves fixture source roles to their runtime canonical source
  IDs and checks required citations are present and forbidden citations are
  absent. It uses the restricted synthetic-evaluation evidence endpoint, never
  the user-facing API.

The follow-up term assertions are deliberately narrow lexical checks. They
create a deterministic floor for known-fact preservation and decision-relevant
questions; physician review still determines clinical usefulness and clarity.

`expected.validation.expected_status` states whether the final provider result
is expected to validate against `ChartReviewOutput`.

## Adding Cases

Use non-identifying keys and source content. Add one case only after it loads
against the existing chart-review contracts and expresses both acceptable
behavior and the failure it guards. Review suite evidence, update the fixture's
human-approved `expected` assertions or add a narrowly scoped case, then rerun
the fast fixture test and the affected local suite. Do not use model output to
silently rewrite expected assertions.
