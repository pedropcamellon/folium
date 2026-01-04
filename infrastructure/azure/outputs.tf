# Output values from the Terraform deployment

output "resource_group_name" {
  description = "Name of the created resource group"
  value       = azurerm_resource_group.south-drift.name
}

# # Commented out - App Service not deployed
# output "app_service_name" {
#   description = "Name of the App Service"
#   value       = azurerm_linux_web_app.south-drift_backend.name
# }
# 
# output "app_service_hostname" {
#   description = "Hostname of the App Service"
#   value       = azurerm_linux_web_app.south-drift_backend.default_hostname
# }
# 
# output "app_service_url" {
#   description = "Full URL of the App Service"
#   value       = "https://${azurerm_linux_web_app.south-drift_backend.default_hostname}"
# }
# 
# output "application_insights_instrumentation_key" {
#   description = "Application Insights instrumentation key"
#   value       = azurerm_application_insights.south-drift.instrumentation_key
#   sensitive   = true
# }
# 
# output "application_insights_connection_string" {
#   description = "Application Insights connection string"
#   value       = azurerm_application_insights.south-drift.connection_string
#   sensitive   = true
# }

# Azure OpenAI Outputs
output "openai_endpoint" {
  description = "Azure OpenAI endpoint URL"
  value       = azurerm_ai_services.openai.endpoint
}

output "openai_api_key" {
  description = "Azure OpenAI API key (primary)"
  value       = azurerm_ai_services.openai.primary_access_key
  sensitive   = true
}

output "openai_deployment_name" {
  description = "GPT-5 Nano deployment name"
  value       = azurerm_cognitive_deployment.gpt5_nano.name
}

output "docker_compose_config" {
  description = "Configuration for docker-compose.yml"
  value = {
    AZURE_OPENAI_ENDPOINT    = azurerm_ai_services.openai.endpoint
    AZURE_OPENAI_KEY         = azurerm_ai_services.openai.primary_access_key
    AZURE_OPENAI_DEPLOYMENT  = azurerm_cognitive_deployment.gpt5_nano.name
    AZURE_OPENAI_API_VERSION = "2024-02-15-preview"
  }
  sensitive = true
}
