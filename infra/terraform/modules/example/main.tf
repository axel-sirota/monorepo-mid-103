# Module: example
#
# A trivial, provider-free module used to prove the /add-terraform-module
# skill output is syntactically valid. Uses null_resource so terraform
# init -backend=false and terraform validate succeed without any cloud creds.

resource "null_resource" "example" {
  triggers = {
    name        = var.name
    environment = var.environment
  }
}
