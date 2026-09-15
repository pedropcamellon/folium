# Lifecycle, citations, and review flags

Chart-review drafts expose state and evidence so a clinician can decide whether
the draft is useful. These fields are review aids, not clinical authority.

## Lifecycle states

- **Processing**: the request is queued or running; completed-only content is
  not shown.
- **Completed**: the structured draft, source references, confidence attribute,
  missing information, follow-up questions, and review flags are available.
- **Failed**: no partial draft is displayed; resolve the reported problem and
  submit a new request.

A new request is clinician-initiated. Creating or editing an interaction does
not silently generate a draft.

## Citations

Source references identify the approved interaction context used by the draft,
such as an interaction title, date, or voice-note transcript role. Compare each
citation with the underlying source. A citation shows provenance; it does not
make a statement clinically authoritative.

## Review flags and confidence

Review flags identify deterministic concerns such as missing information or
validation findings. The confidence value is a draft attribute currently shown
as `low`, `medium`, or `high`; it is not a calibrated clinical risk score.

Before using any draft as working material:

1. Compare claims with the cited synthetic source context.
2. Resolve or document missing information.
3. Correct unsupported or inaccurate text.
4. Make all clinical decisions outside the system.

## Product boundary

Folium is not a complete EHR. It does not support real patient data, diagnosis,
treatment recommendations, or autonomous action.
