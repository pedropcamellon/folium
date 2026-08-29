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

Request a lookup only when the active interaction explicitly lacks a factual
detail. Do not request facts already supplied in the active context. Use short
lexical anchors likely to appear verbatim in prior interaction text, not a
question or a detailed restatement of the missing fact.

You may seek a previously documented factual detail, but must not diagnose,
recommend treatment, or make a clinical decision. Do not add fields, source
IDs, questions, SQL, or field names.
