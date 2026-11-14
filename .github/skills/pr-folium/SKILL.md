---
name: pr-folium
description: Write concise Folium PR bodies and apply the repository PR workflow.
---

# Pull requests

Use [the shared template](../../PULL_REQUEST_TEMPLATE.md) for every PR. Return the
body directly unless asked to create or update a PR. Keep it short.

## Body

- **Summary:** smallest useful diagram, diff-sketch, tree, or brief explanation.
- **Issue:** `Closes #N` only when the PR completes its acceptance criteria;
  otherwise `Refs #N`.
- **Evidence:** verified before/after results only. State when checks were not run.
- **Merge Danger:** `one-way` if reverting cannot fully undo the effects;
  otherwise `two-way`. Preserve uncertainty. Blast radius is one scope word
  (`local`, `service`, `system`); explain only meaningful risks.
- Remove placeholders and omit unsupported claims, secrets, and identifying data.

## Workflow and metadata

- **Scope/title/branch:** one approved slice; title `feat:`, `fix:`, or `chore:`;
  branch `feat/<slug>`, `fix/<slug>`, or `chore/<slug>`.
- **Labels:** reuse existing labels for change type and affected area. Carry over
  applicable issue labels; do not copy issue-only status labels or invent labels.
- **Milestone:** use the linked issue's delivery milestone when applicable.
  Leave unset if none exists; create or change milestones only when asked.
- **Assignee/reviewers:** assignee owns delivery; reviewers check the affected
  area. Set only confirmed people; do not guess.
- **Draft:** use while implementation or validation is incomplete. Mark ready
  when acceptance criteria and required checks are satisfied.
- **Project:** use the linked issue's delivery board when applicable;
  `In Review` when ready, `Done` only after merge and validation.
- **Merge:** resolve review feedback and required checks first. Merge only when
  asked, using repository settings; close only completed issues.
- Before GitHub operations, load and follow the repository-local
  [github-workflow skill](../github-workflow/SKILL.md). Use `gh api` (REST) or
  `gh` CLI commands with the personal account; MCP is fallback only.
  Do not create branches, commits, PRs, or change remote metadata without a request.
