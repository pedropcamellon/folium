# App Service Plan and Backend App

# # App Service Plan (F1 Free Tier)
# resource "azurerm_service_plan" "south-drift" {
#   name                = "asp-south-drift-${var.environment}"
#   resource_group_name = azurerm_resource_group.south-drift.name
#   location            = azurerm_resource_group.south-drift.location
#   os_type             = "Linux"
#   sku_name            = "F1"
# 
#   tags = {
#     environment = var.environment
#     project     = "south-drift"
#     managed-by  = "terraform"
#   }
# }
# 
# # App Service for Backend API
# resource "azurerm_linux_web_app" "south-drift_backend" {
#   name                = "app-south-drift-backend-${var.environment}"
#   resource_group_name = azurerm_resource_group.south-drift.name
#   location            = azurerm_service_plan.south-drift.location
#   service_plan_id     = azurerm_service_plan.south-drift.id
# 
#   site_config {
#     always_on                         = false # F1 plan doesn't support always_on
#     container_registry_use_managed_identity = false
#     
#     application_stack {
#       dotnet_version = "8.0"
#     }
# 
#     # Enable CORS for frontend communication
#     cors {
#       allowed_origins     = var.frontend_urls
#       support_credentials = true
#     }
#   }
# 
#   app_settings = {
#     "ASPNETCORE_ENVIRONMENT" = var.environment
#     "WEBSITES_ENABLE_APP_SERVICE_STORAGE" = "false"
#     # Add your application-specific settings here
#     # "API_KEY" = "@Microsoft.KeyVault(SecretUri=${azurerm_key_vault_secret.api_key.id})"
#   }
# 
#   # Enable Application Insights if needed
#   # identity {
#   #   type = "SystemAssigned"
#   # }
# 
#   tags = {
#     environment = var.environment
#     project     = "south-drift"
#     managed-by  = "terraform"
#   }
# }
