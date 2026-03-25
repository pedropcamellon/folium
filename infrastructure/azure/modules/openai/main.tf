resource "azurerm_ai_services" "this" {
  name                = var.name
  location            = var.location
  resource_group_name = var.resource_group_name
  sku_name            = var.sku_name

  custom_subdomain_name = var.custom_subdomain_name

  identity {
    type = "SystemAssigned"
  }

  tags = var.tags
}

resource "azurerm_cognitive_deployment" "this" {
  for_each = var.deployments

  name                 = each.value.name
  cognitive_account_id = azurerm_ai_services.this.id

  model {
    format  = each.value.model_format
    name    = each.value.model_name
    version = each.value.model_version
  }

  scale {
    type     = each.value.scale_type
    capacity = each.value.scale_capacity
  }

  version_upgrade_option = each.value.version_upgrade_option
}