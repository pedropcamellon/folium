# Folium — GitHub Project Board Layout

A single GitHub Project (board view) replaces the high-level PLAN dashboard. This file is the
source-of-truth definition for how to configure it; the live board lives in GitHub.

## Board: "Folium Delivery"

### Views

1. **Board (by Status)** — primary kanban view, grouped by `Status`.
2. **Table (all fields)** — triage and bulk editing.
3. **Roadmap (by Milestone)** — timeline across milestones.
4. **By Area** — grouped by `Area` to balance load across the stack.

### Custom Fields

| Field            | Type          | Options / Notes                                                                                                                                 |
| ---------------- | ------------- | ----------------------------------------------------------------------------------------------------------------------------------------------- |
| `Status`         | Single select | Backlog, Spec, Ready, In Progress, In Review, Done                                                                                              |
| `Priority`       | Single select | P0 (now), P1 (next), P2 (soon), P3 (someday)                                                                                                    |
| `Area`           | Single select | Auth/RBAC, Patients, Interactions, Documents, Voice Notes, Summarization, Transcription, Temporal, Infra, Observability, E2E, Frontend, Backend |
| `Beta-readiness` | Single select | Blocking, Nice-to-have, Out-of-scope                                                                                                            |
| `Owner`          | Text/Assignee | Solo project: usually self; left for future contributors                                                                                        |
| `Estimate`       | Single select | XS, S, M, L, XL                                                                                                                                 |

### Status Definitions

- **Backlog** — captured, not yet specified.
- **Spec** — spec agent writing/refining acceptance criteria (top zone of task file).
- **Ready** — acceptance criteria signed off; safe for the code agent to start.
- **In Progress** — code agent implementing below the dev-zone marker.
- **In Review** — PR open; spec agent reviewing against acceptance criteria.
- **Done** — merged, validated, task-file checklist complete.

## Milestones (group related work)

- **Voice Notes v2** — `area:voice-notes`, `area:transcription`, `area:summarization`, `area:temporal`.
- **RBAC Phase 2** — `area:auth` (granular permissions beyond admin/provider/staff/patient).
- **Multi-Cloud Hardening** — `area:infra` (AWS + Azure Terraform parity).
- **Observability Baseline** — `area:observability` (Prometheus/Grafana/Promtail dashboards + alerts).
- **E2E Coverage** — `area:e2e` (provider + patient portal flows).

## Suggested Initial Seed (current features → Issues)

See the `tasks/active/` and `tasks/staging/` drafts. Promote each to a GitHub Issue, set
`Area`, `Priority`, `Status`, and assign to a Milestone. Recommended starter set:

| Draft task file                    | Area          | Suggested Milestone    |
| ---------------------------------- | ------------- | ---------------------- |
| `active/feat-auth-rbac.md`         | Auth/RBAC     | RBAC Phase 2           |
| `active/feat-patients-crud.md`     | Patients      | (baseline)             |
| `active/feat-interactions.md`      | Interactions  | (baseline)             |
| `staging/feat-documents.md`        | Documents     | (baseline)             |
| `active/feat-voice-notes.md`       | Voice Notes   | Voice Notes v2         |
| `active/feat-temporal-workflow.md` | Temporal      | Voice Notes v2         |
| `staging/feat-observability.md`    | Observability | Observability Baseline |
| `staging/feat-multicloud-infra.md` | Infra         | Multi-Cloud Hardening  |
| `staging/feat-e2e-suite.md`        | E2E           | E2E Coverage           |
