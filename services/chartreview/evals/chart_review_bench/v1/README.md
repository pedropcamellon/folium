# ChartReviewBench-v1

Committed anonymized chart-review benchmark cases. Each `patient-###`
directory is one case and contains a `case.yaml` seed plan.

`case.yaml` contains non-identifying patient attributes, chronological
encounters, one active encounter, and deterministic output, history, and
validation assertions. The fixture loader validates the plan without touching
persistence. A future staging adapter will create isolated records from the
same plan and execute the workflow.

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
