# Output values from the Terraform deployment

output "resource_group_name" {
  description = "Name of the created resource group"
  value       = module.resource_group.name
}

output "acr_name" {
  description = "Name of the Azure Container Registry"
  value       = try(module.acr[0].name, null)
}

output "acr_login_server" {
  description = "Login server for the Azure Container Registry"
  value       = try(module.acr[0].login_server, null)
}

output "container_app_name" {
  description = "Name of the backend Container App"
  value       = try(module.backend_container_app[0].name, null)
}

output "container_app_fqdn" {
  description = "FQDN of the backend Container App"
  value       = try(module.backend_container_app[0].latest_revision_fqdn, null)
}

output "container_apps_environment_name" {
  description = "Name of the Container Apps environment"
  value       = try(module.container_apps_env[0].name, null)
}

output "key_vault_name" {
  description = "Name of the Key Vault"
  value       = try(module.key_vault[0].name, null)
}

output "key_vault_uri" {
  description = "Vault URI of the Key Vault"
  value       = try(module.key_vault[0].vault_uri, null)
}

output "postgres_host" {
  description = "FQDN of the PostgreSQL Flexible Server"
  value       = try(module.postgres[0].fqdn, null)
}

output "postgres_database_name" {
  description = "Database name for PostgreSQL Flexible Server"
  value       = try(module.postgres[0].database_name, null)
}

output "static_web_app_name" {
  description = "Name of the Static Web App"
  value       = try(module.static_web_app[0].name, null)
}

output "static_web_app_default_hostname" {
  description = "Default hostname of the Static Web App"
  value       = try(module.static_web_app[0].default_host_name, null)
}

output "openai_endpoint" {
  description = "Azure OpenAI endpoint URL"
  value       = try(module.openai[0].endpoint, null)
}

output "openai_api_key" {
  description = "Azure OpenAI API key (primary)"
  value       = try(module.openai[0].primary_access_key, null)
  sensitive   = true
}

output "openai_deployment_name" {
  description = "GPT-5 Nano deployment name"
  value       = try(module.openai[0].deployment_names["gpt5_nano"], null)
}

output "docker_compose_config" {
  description = "Configuration for docker-compose.yml"
  value = {
    AZURE_OPENAI_ENDPOINT    = try(module.openai[0].endpoint, null)
    AZURE_OPENAI_KEY         = try(module.openai[0].primary_access_key, null)
    AZURE_OPENAI_DEPLOYMENT  = try(module.openai[0].deployment_names["gpt5_nano"], null)
    AZURE_OPENAI_API_VERSION = "2024-02-15-preview"
  }
  sensitive = true
}
