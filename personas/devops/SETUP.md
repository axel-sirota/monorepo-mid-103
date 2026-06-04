# DevOps persona — pre-class setup

## Required

- Docker Desktop 25+
- Terraform 1.7+ (`brew install terraform` on macOS)
- Claude Code CLI

## Pre-class warm-up

```bash
cd infra/terraform
terraform init                                # downloads providers (none yet at INITIAL)
terraform fmt -check                          # confirms formatting
```

You won't have anything to plan or apply at INITIAL — that's what 102 builds.
