# Outputs from the example module.

output "resource_id" {
  description = "The ID of the null_resource provisioned by this module"
  value       = null_resource.example.id
}
