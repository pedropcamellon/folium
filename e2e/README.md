# SouthDrift E2E

SouthDrift E2E checks focus on one thing: proving role-aware UX with realistic user behavior.

This suite validates two visible user journeys:

- Provider signs in, lands on the provider experience, creates a patient, updates that patient, deletes that patient, then signs out.
- Patient signs in, lands on the patient portal, and signs out.

The goal is fast confidence for demos and regressions, not exhaustive coverage.

Design principles:

- Reusable flow modules instead of one large script.
- Assertions aligned to stable UI landmarks.
- Human-observable runs by default so behavior is easy to verify live.

Expected outcome: a quick pass/fail signal that role routing, session boundaries, and core provider CRUD interactions still work end to end.
