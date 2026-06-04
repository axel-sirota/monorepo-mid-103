# pm/ — what this pack installs

`/set-persona pm` copies `starter-files/` into `.claude/`. Empty at INITIAL.

## Mid pack (end of 102)

- `agents/pm-prds.md` — prds-scoped subagent (no Bash)
- `agents/pm-dev-perspective.md` — Three Amigos teammate
- `agents/pm-qa-perspective.md` — Three Amigos teammate
- `agents/pm-gap-detector.md` — Three Amigos teammate
- `skills/decompose-epic/SKILL.md` — parallel dispatch of the three above
- `hooks/pm-check.sh` — pre-commit G/W/T gate on `prds/*.md`

## End pack (end of 103)

Adds 4 review subagents (INVEST, NFR, edge-case, dependency).

## MCPs

`atlassian` (Jira/Confluence — optional), `github-issues`, `slack` (optional).
