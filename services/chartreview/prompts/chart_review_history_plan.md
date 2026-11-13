# Chart Review Evidence Plan

Decide whether one missing factual detail in the active interaction could be
clarified from approved prior interactions. Do not select search terms yet.

Return valid JSON in exactly one of these forms:

```json
{
  "outcome": "search_history",
  "factual_gap": "The active interaction does not identify the prescribed inhaler.",
  "evidence_objective": "Find a previously documented inhaler name.",
  "evidence_scope": "approved_prior_interactions",
  "success_condition": "approved_block_returned",
  "stop_policy": "bounded_history"
}
```

```json
{
  "outcome": "no_search",
  "reason": "active_context_sufficient"
}
```

Use `permitted_history_not_useful` when a lookup cannot help. Plan one factual
gap only. Search only for a previously documented fact; do not diagnose,
recommend treatment, make clinical decisions, or request documents or other
evidence. Return concise fields, not hidden reasoning. Do not add fields,
queries, tools, or source identifiers.
