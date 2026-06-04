# example

## Purpose

A trivial, provider-free terraform module that proves the canonical module
layout (and the `/add-terraform-module` skill output) is syntactically valid.
It uses `null_resource` so that `terraform init -backend=false` and
`terraform validate` succeed without any cloud credentials configured.

Use it as a smoke test: if `validate` passes here, the scaffold is wired
correctly. Delete or replace once you have real modules.

## Usage

```hcl
module "example" {
  source = "./modules/example"

  name        = "smoke-test"
  environment = "dev"
}
```

## Inputs

| Name | Type | Default | Description |
|---|---|---|---|
| `name` | `string` | (required) | Name of this example instance |
| `environment` | `string` | `"dev"` | Deployment environment |

## Outputs

| Name | Description |
|---|---|
| `resource_id` | The ID of the null_resource provisioned by this module |

## Validation

From the module directory:

```
terraform init -backend=false
terraform validate
```

Both commands should exit 0. If they don't, the scaffold has drifted.
