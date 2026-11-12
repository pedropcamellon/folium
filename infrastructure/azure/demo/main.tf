locals {
  tags = {
    application = "folium"
    environment = "demo"
    data        = "synthetic"
    managed_by  = "terraform"
  }
}

module "resource_group" {
  source = "../modules/resource_group"

  name     = var.resource_group_name
  location = var.location
  tags     = local.tags
}

resource "azurerm_service_plan" "container_demo" {
  count = var.enable_app_service_demo ? 1 : 0

  name                = var.app_service_plan_name
  resource_group_name = module.resource_group.name
  location            = module.resource_group.location
  os_type             = "Linux"
  sku_name            = "F1"
  tags                = local.tags
}

resource "azurerm_linux_web_app" "container_demo" {
  count = var.enable_app_service_demo ? 1 : 0

  name                = var.app_service_name
  resource_group_name = module.resource_group.name
  location            = module.resource_group.location
  service_plan_id     = azurerm_service_plan.container_demo[0].id
  https_only          = true
  tags                = local.tags

  site_config {
    always_on        = false
    app_command_line = "node server.js"

    application_stack {
      node_version = "20-lts"
    }
  }

  app_settings = {
    PORT                           = "8080"
    HOSTNAME                       = "0.0.0.0"
    SCM_DO_BUILD_DURING_DEPLOYMENT = "false"
  }
}
