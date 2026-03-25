output "id" {
  value = azurerm_ai_services.this.id
}

output "name" {
  value = azurerm_ai_services.this.name
}

output "endpoint" {
  value = azurerm_ai_services.this.endpoint
}

output "primary_access_key" {
  value     = azurerm_ai_services.this.primary_access_key
  sensitive = true
}

output "deployment_names" {
  value = {
    for deployment_key, deployment in azurerm_cognitive_deployment.this : deployment_key => deployment.name
  }
}