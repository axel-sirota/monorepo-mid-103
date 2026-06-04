# engineer/ — what this pack installs

Running `/set-persona engineer` copies `starter-files/` into the project's `.claude/`. At INITIAL stage, `starter-files/` is empty. The packs you build in 102 and 103 land here.

## Mid (end of 102) — pack contents

- `agents/engineer-apps.md` — service-scoped subagent with `isolation: worktree`
- `skills/add-endpoint/SKILL.md` (+ templates) — TDD endpoint procedure
- `hooks/engineer-check.sh` — pre-commit gate for `apps/` changes

## End (end of 103) — pack contents

Adds:

- `agents/engineer-security-reviewer.md`
- `agents/engineer-performance-reviewer.md`
- `agents/engineer-style-reviewer.md`
- `agents/engineer-test-reviewer.md`
- `/review-pr` orchestrator (in `.claude/commands/`)
- `model:` frontmatter applied to `/architect`, `/start-session`, `/research`, `/code-review`

## MCPs

`mcp.json` in this directory lists the MCP servers the engineer persona uses. At INITIAL: `github`, `postgres`, `playwright`. Replace via `client-config/personas/engineer/mcp.json` for client-specific endpoints (e.g. GitHub Enterprise).
