---
name: github-workflow
description: >
  Interact with the Folium GitHub remote (issues, branches, PRs, labels) for the
  spec-driven workflow. PREFER the GitHub REST API via the `gh` CLI; use the GitHub
  MCP server only as a fallback when `gh`/REST is unavailable. WHEN: create/close issue,
  comment on issue/PR, create/rename/delete branch, manage labels/milestones, push
  roadmap or shipped features to GitHub, mirror Issues into local task files.
---

# github-workflow — command reference

Terse tool syntax only. Policy/behavior (which account, when to use, branch policy)
lives in the agent instructions, not here.

## Identity

```bash
gh api user --jq .login
```

## Issues

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

```bash
gh pr list --state all
gh pr view <n>
gh pr create -t "TITLE" -F body.md -B main -H <branch>
```

## Branches (git)

```bash
git push origin <sha>:refs/heads/<branch>          # create
git push origin origin/<old>:refs/heads/<new>      # copy (rename step 1)
git push origin --delete <branch>                  # delete
git ls-remote --heads origin | awk '{print $2}'    # list remote
```

## Labels

```bash
gh label list
gh label create <name> -c <hex> -d "<desc>"
gh label edit <name> --name <new> --color <hex>
gh label delete <name>
```

## Milestones (REST)

```bash
gh api repos/{owner}/{repo}/milestones -f title="TITLE" -f state=open
gh api repos/{owner}/{repo}/milestones --jq '.[].title'
```

## MCP fallback tools (use only if gh/REST unavailable)

`get_me`, `list_issues`, `issue_write`, `add_issue_comment`, `create_branch`,
`list_pull_requests`. Not available via MCP: label write, milestone write, branch delete.
