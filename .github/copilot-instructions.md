# Copilot Instructions — Folium

Personal project. Use your personal GitHub account for all git/remote ops, never a work account.

## Architecture

- Monorepo: `backend/` (FastAPI, Python 3.11+), `frontend/` (Next.js App Router + shadcn/ui), AI microservices (voice transcription, medical imaging) orchestrated by backend.
- Mock data lives in backend; frontend fetches via service modules.

## Rules

- API Calls: Use centralized API configuration never hardcode API URLs in components.
- Frontend types must match backend models exactly (field names, data types). When changing backend models, update frontend types immediately
- Types: Frontend types must match backend models exactly. Update both when changing either
- Code examples in docs: Only short snippets (5-10 lines) to illustrate patterns
- No PII: Never include personal names, company names, or identifiable information in public repo files
- No emojis: Never use emojis in code generation (comments, strings, logs, or documentation). Use clear descriptive text instead.
- Assistant Responses: Always include datetime footer in ISO 8601 format (YYYY-MM-DD HH:MM)

## Input Sanitization

- Repo layer = defense-in-depth: strip whitespace, validate UUIDs, normalize "null"→None, isinstance checks, log Pydantic misses.
- Datetime: pass datetime objects (Pydantic converts); service layer must not `.isoformat()`.
- Max lengths in Pydantic, not repos. ORM params stop SQLi; frontend stops XSS (backend stores raw).

## GitHub Workflow

- Prefer `gh` CLI / REST; MCP server only as fallback. Command syntax in the `github-workflow` skill.
- On macOS, use `grep` for repository text searches; do not assume `rg` is installed.
- Branches: `feat/<slug>`, `chore/<slug>`, `fix/<slug>`. Rename = create new ref + delete old.
- Issues: shipped work = closed issue (`-r completed`); in-flight = open issue referencing its `feat/*` branch. Mirror each to `tasks/<active|staging|completed>/<issue>-<slug>.md` (`tasks/_TEMPLATE.md`); move between folders as state changes.
- Labels/milestones via `gh` (not MCP); seed set in `tasks/PROJECT-BOARD.md`.
