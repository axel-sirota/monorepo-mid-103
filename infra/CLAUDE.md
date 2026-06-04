# infra/ — devops cluster

Lazy-loaded by Claude Code when working with files under `infra/`. The root `/CLAUDE.md` still loads first.

## Layout

```
infra/
├── terraform/
│   ├── main.tf              # root module — wires module instances
│   ├── variables.tf
│   ├── outputs.tf
│   └── modules/             # populated by /add-terraform-module skill
│       └── {module-name}/
│           ├── main.tf
│           ├── variables.tf
│           ├── outputs.tf
│           ├── versions.tf
│           └── README.md
├── terraform_plans/         # GITIGNORED — plan output files
└── docker/
    └── postgres-init/
        └── 01-create-databases.sql
```

## Hard rules

These are mechanical, not behavioural. Three of them are enforced by `.claude/settings.json` `permissions.deny`; the orchestrator-level harness refuses outright.

- **Plan before apply. Always.** Every `terraform apply` runs against a saved plan file:
  ```
  terraform plan -out=terraform_plans/$(date +%Y%m%d-%H%M%S).tfplan
  terraform apply terraform_plans/{the-plan-just-saved}.tfplan
  ```
  Never `terraform apply` without a `-out` reference. There is no "quick apply" — convenience here is how state gets corrupted.

- **Never destroy yourself.** `terraform destroy` is human-only. The `permissions.deny` rule in `.claude/settings.json` blocks Claude from invoking it. This is mechanical enforcement, not a behavioural reminder.

- **State files are sacred.** Never delete a `.tfstate`. Never commit a `.tfstate`. The pre-commit hook (`devops-check.sh`, lab 3) refuses to stage any `*.tfstate` or `*.tfstate.backup`. State lives on disk and is managed by Terraform itself, not by Claude.

## Terraform workflow

```
cd infra/terraform
terraform init                                              # only when modules change
terraform fmt
terraform validate
terraform plan -out=terraform_plans/$(date +%Y%m%d-%H%M%S).tfplan
terraform apply terraform_plans/{the-plan-just-saved}.tfplan   # human-run only
```

Plans go to `infra/terraform_plans/` (gitignored). The devops pre-commit hook blocks `.tf` commits unless a fresh `.tfplan` exists in `terraform_plans/` that is newer than the staged `.tf` file.

## Module conventions

- Each module gets its own subdirectory under `infra/terraform/modules/{name}/`.
- Every module ships: `main.tf`, `variables.tf`, `outputs.tf`, `versions.tf`, `README.md`, and an `examples/` directory once the module has real consumers.
- Every `variable` has a `description` AND a `type`.
- Every `output` has a `description`.
- Provider versions are pinned in `versions.tf`.

Use the `/add-terraform-module` skill (lab 2) to scaffold new modules — it sets up the canonical layout, runs `fmt + init + validate`, and produces a saved plan.

## Secrets

Secrets stay out of state. Use provider-native secret references (e.g. AWS Secrets Manager via `data "aws_secretsmanager_secret_version"`, GCP Secret Manager via `data "google_secret_manager_secret_version"`), not literals in `.tf` files. Anything literal here ends up in plaintext in the state file.

## Local backend at MID stage

The Terraform backend is `local` at MID (no remote state). Migrating to a remote backend (S3, GCS, ...) is out of scope for 102 — it lands in 103 alongside CI/CD.

## Active subagent

`devops-infra` — scoped to this cluster. Tools: `Read, Glob, Grep, Edit, Write, Bash`. Bash sub-command restrictions (no `terraform destroy`, no `rm`, no `terraform state rm`) live in `.claude/settings.json` `permissions.deny`, not in the agent itself.

## Skill

`/add-terraform-module <name>` — scaffolds a module + runs validate + saves a plan. Does NOT apply.

## What's NOT here

- No real cloud provider config. The Terraform at MID is local-stub for teaching workflow discipline.
- No CI/CD pipelines (those live in adapt-to-your-codebase docs and arrive in 103).
- No remote backend.
