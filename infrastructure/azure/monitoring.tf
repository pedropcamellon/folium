# Application Insights and Log Analytics

# resource "azurerm_log_analytics_workspace" "south-drift" {
#   name                = "log-south-drift-${var.environment}"
#   location            = azurerm_resource_group.south-drift.location
#   resource_group_name = azurerm_resource_group.south-drift.name
#   sku                 = "PerGB2018"
#   retention_in_days   = 30
#   tags = {
#     environment = var.environment
#     project     = "south-drift"
#     managed-by  = "terraform"
#   }
# }
# 
# resource "azurerm_application_insights" "south-drift" {
#   name                = "appi-south-drift-${var.environment}"
#   location            = azurerm_resource_group.south-drift.location
#   resource_group_name = azurerm_resource_group.south-drift.name
#   application_type    = "web"
#   workspace_id        = azurerm_log_analytics_workspace.south-drift.id
# 
#   tags = {
#     environment = var.environment
#     project     = "south-drift"
#     managed-by  = "terraform"
#   }
# }
