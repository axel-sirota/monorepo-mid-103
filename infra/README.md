# infra/

DevOps persona's home cluster. At the INITIAL stage this is intentionally a stub: a local-backend Terraform skeleton and the Postgres init SQL that docker-compose mounts.

Real modules get built in the 102 devops lab (`add-terraform-module` skill).

## Layout

```
infra/
├── terraform/
│   ├── main.tf          # backend "local" — no remote state at INITIAL
│   ├── variables.tf
│   ├── outputs.tf
│   └── modules/         # empty; populated in 102 devops lab
└── docker/
    └── postgres-init/
        └── 01-create-databases.sql   # creates users_db, notifications_db, mlflow_db
```

## Running terraform

Not part of `make up`. The terraform stub exists so the devops persona has a place to land their first module.

```bash
cd infra/terraform
terraform init
terraform plan -out=../terraform_plans/$(date +%Y%m%d-%H%M).tfplan
```

Plans go to `infra/terraform_plans/` (gitignored). Never apply outside a saved plan.
