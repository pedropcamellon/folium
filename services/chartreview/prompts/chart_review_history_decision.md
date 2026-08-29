# Chart Review History Decision

Decide whether one prior-interaction history lookup would clarify a factual gap.

Return valid JSON only with this exact shape:

```json
{
  "search_terms": ["inhaler", "prescription"]
}
```

Use one to three concise terms that may locate a missing factual detail in
prior interactions. Return an empty `search_terms` list when no lookup is
needed.

Do not request a lookup for diagnosis, treatment, recommendation, or ambiguous
information. Do not add fields, source IDs, questions, SQL, or field names.
