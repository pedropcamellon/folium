---
applyTo: "{**/{test_*,*_test}.py,e2e/**/*.py}"
description: "Use when editing tests or end-to-end flows in Folium."
---

- Prefer one focused end-to-end test that proves the user-visible workflow over multiple unit tests of internal boundaries.
- Add a unit test only for deterministic, pure behavior that a focused E2E flow cannot reasonably cover.
- Use synthetic fixtures only. Do not add real patient data, identifiers, or production credentials to tests.
- For agent behavior, use offline evaluation and traceable expected properties; do not treat a passing deterministic mock as evidence that a probabilistic provider is safe.
- Assert explicit failure and human-review states. Do not accept silent partial output or autonomous clinical actions.