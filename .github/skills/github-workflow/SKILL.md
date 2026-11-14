---
name: github-workflow
description: >
  Interact with the Folium GitHub remote (issues, branches, PRs, labels) for the
  spec-driven workflow. PREFER the GitHub REST API via the `gh` CLI; use the GitHub
  MCP server only as a fallback when `gh`/REST is unavailable. WHEN: create/close issue,
  comment on issue/PR, create/rename/delete branch, manage labels/milestones, push
  roadmap or shipped features to GitHub, mirror Issues into local task files.
---

# GitHub workflow

Use `gh api` for REST operations or the dedicated `gh` CLI command when simpler.
Use GitHub MCP only if `gh`/REST is unavailable, not to bypass permissions.
Read current remote state before writing; verify the changed fields afterward.
Report failed operations explicitly. Do not claim a remote update succeeded
without confirmation.

## Identity

Verify the authenticated user and target repository before remote writes. Use
the personal account only; stop if a work account is active. Use explicit
`--repo <owner>/<repo>` or REST repository paths when the target is ambiguous.
Change remote state only when requested; do not create commits or branches
as a side effect of drafting an issue or PR.

```bash
gh api user --jq .login
```

## Issues

The issue is the durable source of truth. Read it before implementation; use
`## Description` and `## Acceptance Criteria`. Record accepted decisions,
blockers, scope changes, and verified evidence there. Search for existing work
before creating a duplicate. Keep partial work open; close as completed only
when acceptance criteria are met and delivery is validated.
An active local task, when present, references the issue and tracks the current
slice; it does not duplicate the issue.

```bash
gh issue list
gh issue view <n>
gh issue create -t "TITLE" -F body.md
gh issue close <n> -r completed
gh issue reopen <n>
gh issue comment <n> -b "TEXT"
gh issue edit <n> --add-label <label> --milestone "<title>"
```

## Pull requests

Load the repository-local [pr-folium skill](../pr-folium/SKILL.md) and use the shared template.
Keep one approved slice per PR. Use `Refs #N` for partial work and `Closes #N`
only for completed acceptance criteria. Confirm the base and head branches;
do not assume `main` if the repository uses another target.
Open as draft when implementation or validation is incomplete. Before merging,
verify required checks and resolve review feedback. Merge only when asked,
using the repository's allowed merge method.

```bash
gh pr list --state all
gh pr view <n>
gh pr create -t "TITLE" -F body.md -B main -H <branch>
```

## Branches (git)

Use `feat/<issue>-<slug>`, `fix/<issue>-<slug>`, or `chore/<issue>-<slug>`
when the branch is tied to an issue (for example, `feat/123-patient-search`).
For work without an issue, omit the number. Inspect existing refs first.
For renames, confirm the source and ensure the destination does not exist;
create the new ref, verify it, then delete the old ref only when authorized.
Do not overwrite existing refs or delete branches implicitly.

```bash
git push origin <sha>:refs/heads/<branch>          # create
git push origin origin/<old>:refs/heads/<new>      # copy (rename step 1)
git push origin --delete <branch>                  # delete
git ls-remote --heads origin | awk '{print $2}'    # list remote
```

## Labels

List existing labels first. Reuse change-type and affected-area labels on
issues and PRs; carry applicable labels from the linked issue, not issue-only
status labels. Create, rename, or delete labels only when requested.
Labels classify work; use project Status for delivery progress.

```bash
gh label list
gh label create <name> -c <hex> -d "<desc>"
gh label edit <name> --name <new> --color <hex>
gh label delete <name>
```

## Milestones (REST)

Milestones group a delivery goal or release, not workflow status. Reuse the
linked issue's milestone on its PR when applicable; leave unset if none exists.
Inspect existing milestones before assigning one. Create or change milestone
definitions only when requested; do not invent dates or delivery commitments.

```bash
gh api repos/{owner}/{repo}/milestones -f title="TITLE" -f state=open
gh api repos/{owner}/{repo}/milestones --jq '.[].title'
```

## Ownership and project status

Set assignees and reviewers only when confirmed: assignees own delivery,
reviewers check the affected area. Use the linked issue's delivery project when
applicable. Follow `Backlog -> Spec -> Ready -> In Progress -> In Review -> Done`;
move to `In Review` when ready for review, and `Done` after merge and validation.
Update project fields through `gh project` or `gh api`; inspect item and field
IDs before writing. Leave unrelated metadata unchanged.
