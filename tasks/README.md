# Folium Task Files

Local working memory for the spec-driven + test-backed workflow. Each work item gets one
file: `<staging|active|completed>/<ID>-<slug>.md`. The numeric ID matches the GitHub Issue
number when one exists (e.g. `active/42-voice-notes.md` mirrors Issue #42); drafts that
predate an Issue use a short slug (e.g. `staging/feat-observability.md`).

> Task files are git-ignored; only this README, `_TEMPLATE.md`, `PROJECT-BOARD.md`, and the
> folder layout (`.gitkeep`) are tracked. Task files are personal working memory, not shared
> source. Durable knowledge is promoted to GitHub Issues/PRs, Discussions, or `docs/`.

## Folder Layout

Files move between three root folders as work progresses (move the file, don't just edit a
status field — the folder is the at-a-glance dashboard):

```
tasks/
  staging/     # backlog / drafts not yet started
  active/      # in-progress, blocked, or in-review work
  completed/   # done; kept as historical record
  _TEMPLATE.md
  PROJECT-BOARD.md
  README.md
```

## Two-Zone Format

Every task file has two zones separated by the `--- DEV / CODING AGENT ZONE ---` marker:

- **Top (PM / spec zone)** — owned by the spec agent and the user:
  - Status, Owner, Parent, Description, Acceptance Criteria, Children, Linked PRs/Commits, Notes.
  - PM-language intent. The code agent reads but does not edit this zone.
- **Below the marker (dev zone)** — owned by the code agent:
  - Progress checklist, Implementation Notes, Changed Files, Blockers, Next Action.

Use `_TEMPLATE.md` as the starting point.

## GitHub Mapping (replaces ADO)

| Need                           | GitHub equivalent                            |
| ------------------------------ | -------------------------------------------- |
| Work item tracking             | Issues + Labels + Projects board             |
| Cross-task memory & history    | Issue comments + PR comments + linked issues |
| Future ideas / open questions  | Discussions + `future-idea` labeled Issues   |
| Sprint/portfolio dashboard     | GitHub Projects (see `PROJECT-BOARD.md`)     |
| PR reviews & threading         | GitHub PR reviews + comment threads          |
| Durable architecture knowledge | `docs/` + repo `SPEC.md` files               |

### Labels

`spec`, `implementation`, `bug`, `future-idea`, `blocked`, plus area labels:
`area:auth`, `area:patients`, `area:interactions`, `area:documents`,
`area:voice-notes`, `area:summarization`, `area:transcription`, `area:temporal`,
`area:infra`, `area:observability`, `area:e2e`, `area:frontend`, `area:backend`.

## Workflow Loop

1. Start from a GitHub Issue or a new draft in `staging/` (copy `_TEMPLATE.md`).
2. Spec agent writes/refines the contract (top zone); move file to `active/` when Ready.
3. Code agent implements below the marker and records evidence.
4. Capture history and deferred follow-ups in Issue/PR comments.
5. Promote durable knowledge to repo `SPEC.md` files or `docs/`.
6. Close the loop: tick the Progress checklist, move the file to `completed/`, update the board.

## Roles

- **Spec agent** — owns acceptance criteria, top zone, PR reviews, Issue drafts.
- **Code agent** — works below the marker; touches code + task files only.
- **User** — owns commits, phase sign-off, and persistent directives.
