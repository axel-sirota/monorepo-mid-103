# designer/ — what this pack installs

`/set-persona designer` copies `starter-files/` into `.claude/`. Empty at INITIAL.

## Mid pack (end of 102)

- `agents/designer-frontend.md` — frontend-scoped subagent
- `skills/extract-figma-frame/SKILL.md` — Figma → context
- `hooks/designer-check.sh` — pre-commit token-discipline gate

## End pack (end of 103)

Adds 4 review subagents (a11y, responsive, token-drift, visual-regression).

## MCPs

`figma`, `playwright`. Figma needs `FIGMA_ACCESS_TOKEN` and Figma desktop running.
