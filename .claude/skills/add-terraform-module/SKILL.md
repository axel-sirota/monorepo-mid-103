---
name: add-terraform-module
description: Scaffold a new terraform module under infra/terraform/modules/{name}/ with canonical files (main.tf, variables.tf, outputs.tf, versions.tf, README.md), run fmt + init + validate, then generate a saved plan. Does NOT apply. Use when the user asks to add a terraform module, scaffold infrastructure, or create a new IaC component.
allowed-tools: Read, Edit, Write, Bash
---

# Add a Terraform module (scaffold + validate + plan)

You are scaffolding a new terraform module. This skill produces a canonical module skeleton, validates it, wires it into the root, and saves a plan — it never applies.

## Step 0 — Get the module name

Ask the user for the module name if not already provided. The name MUST be `kebab-case` (lowercase letters, digits, hyphens). If the user gives a name that is not kebab-case, normalise it and confirm before proceeding.

If the directory `infra/terraform/modules/{name}/` already exists and is non-empty, STOP and ask — do not overwrite.

## Step 1 — Create the module directory

```
mkdir -p infra/terraform/modules/{name}
```

## Step 2 — Scaffold from templates

Render each of these template files from `${CLAUDE_SKILL_DIR}/templates/` into the new module directory. Replace the `{{MODULE_NAME}}` token with the module name everywhere it appears.

| Template | Target |
|---|---|
| `main.tf.template` | `infra/terraform/modules/{name}/main.tf` |
| `variables.tf.template` | `infra/terraform/modules/{name}/variables.tf` |
| `outputs.tf.template` | `infra/terraform/modules/{name}/outputs.tf` |
| `versions.tf.template` | `infra/terraform/modules/{name}/versions.tf` |
| `README.md.template` | `infra/terraform/modules/{name}/README.md` |

## Step 3 — Format the module in place

```
cd infra/terraform/modules/{name} && terraform fmt
```

## Step 4 — Initialise the module standalone (no backend)

```
cd infra/terraform/modules/{name} && terraform init -backend=false
```

This downloads any providers declared in `versions.tf`. The `-backend=false` flag skips backend wiring — we only want to validate the module, not provision state for it directly.

## Step 5 — Validate the module standalone

```
cd infra/terraform/modules/{name} && terraform validate
```

If validate fails, STOP and report the error to the user. Do not proceed to wiring or planning.

## Step 6 — Wire the module into the root

Edit `infra/terraform/main.tf` to add a module block referencing the new module:

```hcl
module "{name}" {
  source = "./modules/{name}"

  # Required inputs (uncomment and fill once the module declares them):
  # name = "{name}-default"
}
```

Place the block near other `module` blocks if any exist; otherwise, after the `terraform { ... }` block.

## Step 7 — Run full root init

```
cd infra/terraform && terraform init
```

This picks up the new module reference in `main.tf`.

## Step 8 — Save a plan

```
cd infra/terraform && mkdir -p terraform_plans && terraform plan -out=terraform_plans/$(date +%Y%m%d-%H%M%S).tfplan
```

The plan goes to `infra/terraform_plans/` (gitignored).

## Step 9 — Report back

Tell the user:
- Module directory path: `infra/terraform/modules/{name}/`
- Plan file path: `infra/terraform_plans/{timestamp}.tfplan`
- Summary of what the plan will create (count of resources, names).
- The exact apply command **the human can run themselves**:
  ```
  cd infra/terraform && terraform apply terraform_plans/{timestamp}.tfplan
  ```

## DO NOT

- DO NOT run `terraform apply`. This skill ends with a saved plan; the human applies.
- DO NOT run `terraform destroy`. Ever.
- DO NOT delete `.tfstate*` files. Ever.
- DO NOT commit the `.tfplan` file — it's gitignored and is an audit artefact, not source.
