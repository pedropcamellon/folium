# SouthDrift E2E

SouthDrift E2E checks focus on one thing: proving role-aware UX with realistic user behavior.

This suite validates two visible user journeys:

- Provider signs in, lands on the provider experience, creates a patient, updates that patient, deletes that patient, then signs out.
- Patient signs in, lands on the patient portal, and signs out.

It also includes separate provider voice-note and provider summary scenarios so transcript and summary coverage can evolve independently of patient CRUD.

The goal is fast confidence for demos and regressions, not exhaustive coverage.

Design principles:

- Reusable flow modules instead of one large script.
- Assertions aligned to stable UI landmarks.
- Human-observable runs by default so behavior is easy to verify live.

Current organization:

- `main.py` keeps browser startup and top-level orchestration only.
- `browser_session.py` coordinates shared auth/session flow and runs exactly one scenario at a time.
- `scenarios.py` is the registry for runnable scenarios and scenario selection.
- `flows/` owns isolated business journeys such as patient CRUD, transcript, and summary automation.
- `ui/` owns selectors and page interactions.
- `mocks/` owns targeted network stubs for unstable dependencies.
- `patient_payloads.py` and `flow_cases.py` keep test data and role configuration separate from browser logic.

Run options:

- Run everything: `uv run .\main.py`
- List scenarios: `uv run .\main.py --list`
- Run one scenario: `uv run .\main.py --scenario provider-voice-note`
- Run summary only: `uv run .\main.py --scenario provider-summary`
- Run multiple scenarios: `uv run .\main.py --scenario provider-patient-crud --scenario patient-portal`
- Use env selection instead of flags: set `SOUTHDRIFT_E2E_SCENARIOS=provider-voice-note`

Expected outcome: a quick pass/fail signal that role routing, session boundaries, and core provider CRUD interactions still work end to end.
