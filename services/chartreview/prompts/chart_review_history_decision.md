# Chart Review History Decision

Decide whether one prior-interaction history lookup would clarify a factual gap.

Return valid JSON only with this exact shape:

```json
{
  "search_terms": ["<term>"]
}
```

The shape above is a format placeholder. Never copy `<term>`; select terms only
from the active interaction's own declared gaps. Use one to three concise terms
that may locate a missing factual detail in prior interactions. Prefer a single
word per concept, such as `medication`, `adherence`, or `lisinopril`. Use a
multi-word term only when one word would be too ambiguous. Return an empty
`search_terms` list when no lookup is needed, including any acute, self-contained
active interaction that declares no historical-information gap.

Request a lookup only when the active interaction explicitly lacks a factual
detail. Do not request facts already supplied in the active context. Use short
lexical anchors likely to appear verbatim in prior interaction text, not a
question, synonym, or detailed restatement of the missing fact.

Do not look up an observation that can only be obtained from the patient or
clinician now, such as an unrecorded current measurement or symptom course.
Those are follow-up gaps, not historical-information gaps; return an empty list
unless the active interaction specifically indicates that prior documentation
could supply the missing detail.

You may seek a previously documented factual detail, but must not diagnose,
recommend treatment, or make a clinical decision. Do not add fields, source
IDs, questions, SQL, or field names.
