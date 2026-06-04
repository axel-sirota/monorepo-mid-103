# Inputs for the example module.

variable "environment" {
  description = "Deployment environment for the example module instance"
  type        = string
  default     = "dev"
}

variable "name" {
  description = "Name of this example instance"
  type        = string
}
