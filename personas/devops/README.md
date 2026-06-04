# devops/ — what this pack installs

`/set-persona devops` copies `starter-files/` into `.claude/`. Empty at INITIAL.

## Mid pack (end of 102)

- `agents/devops-infra.md` — infra-scoped subagent with restricted Bash
- `skills/add-terraform-module/SKILL.md` — module scaffolder
- `hooks/devops-check.sh` — pre-commit plan-output gate

## End pack (end of 103)

Adds 4 review subagents (iac-security, cost, drift, compliance).

## MCPs

Empty default. Client-config typically adds Terraform Cloud, AWS, GCP, or internal IaC tooling.
