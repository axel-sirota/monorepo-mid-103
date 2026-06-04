# data-scientist/ — what this pack installs

`/set-persona data-scientist` copies `starter-files/` into `.claude/`. Empty at INITIAL.

## Mid pack (end of 102)

- `agents/data-scientist-ml.md` — ml-scoped subagent
- `skills/log-experiment/SKILL.md` — structured experiment log + MLflow
- `hooks/data-scientist-check.sh` — pre-commit seed/notebook gate

## End pack (end of 103)

Adds 4 review subagents (reproducibility, data-leakage, model-card-completeness, bias).

## MCPs

`filesystem` (scoped to `ml/data/`), `context7`. Client-config can add Snowflake / BigQuery / internal MLflow.
