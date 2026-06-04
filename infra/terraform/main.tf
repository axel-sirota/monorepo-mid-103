terraform {
  required_version = ">= 1.7.0"

  backend "local" {
    path = "terraform.tfstate"
  }
}

# INITIAL stage: no providers configured. Devops persona adds the first
# module + provider in the 102 `add-terraform-module` skill lab.
