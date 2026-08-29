# Chart Review Drafts

## Overview

Chart Review Drafts provide clinician-requested draft support for a selected
interaction. A draft summarizes supplied chart context, identifies information
that was not available, suggests follow-up questions, and lists the sources it
used.

This feature uses synthetic data in the current Folium environment. It does not
diagnose, recommend treatment, or take action. A clinician must review the
draft and make all clinical decisions.

## Request a Draft

1. Open a patient and select an interaction.
2. In the interaction details, find **Chart Review Draft**.
3. Select **Generate draft**. Select **Generate new draft** to request another
   draft after an earlier request has reached a terminal state.
4. Continue working elsewhere while the request is processed.

The draft is requested only when a clinician selects the action. It is not
automatically generated when an interaction is created or edited.

## Review the Result

The chart-review section displays one of these states:

- **Processing**: The request is queued or running. Completed-only content is
  not shown.
- **Completed**: Review the summary, review rationale, missing information,
  follow-up questions, confidence level, source references, and review flags.
- **Failed**: No partial draft is displayed. Submit a new request after the
  reported problem is resolved.

Source references identify the interaction title, date, and the cited content
role, such as summary or voice-note transcript. They identify evidence used for
the draft; they do not make the output clinically authoritative.

## Use Drafts Safely

- Compare the draft against the underlying interaction and cited sources.
- Treat missing information as a gap for clinician review, not as a request the
  system will automatically pursue.
- Confirm medication details, symptoms, and other clinically relevant facts
  before recording or acting on them.
- Do not rely on the confidence label as a clinical risk score. It is a
  model-provided draft attribute and is currently displayed as `low`, `medium`,
  or `high`.

## Current Context Boundary

Each request starts from an immutable snapshot of the selected interaction. The
service can include a small backend-approved set of prior interaction context.
It does not provide unrestricted chart search or document retrieval.

## Planned Capabilities

Folium may later add policy-controlled retrieval of additional approved chart
blocks when a draft identifies missing information. That behavior is not
available today and will require explicit source controls, validation, audit
records, and clinician review before release.

---

**Last Updated**: August 29, 2026
