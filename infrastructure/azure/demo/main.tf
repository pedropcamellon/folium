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

module "static_web_app" {
  source = "../modules/static_web_app"

  name                = var.static_web_app_name
  resource_group_name = module.resource_group.name
  location            = module.resource_group.location
  sku_tier            = "Free"
  sku_size            = "Free"
  tags                = local.tags
}

resource "azurerm_service_plan" "container_demo" {
  count = var.enable_app_service_demo ? 1 : 0

  name                = var.app_service_plan_name
  resource_group_name = module.resource_group.name
  location            = module.resource_group.location
  os_type             = "Linux"
  sku_name            = "B1"
  tags                = local.tags
}

resource "azurerm_container_registry" "demo" {
  count = var.enable_app_service_demo ? 1 : 0

  name                = var.container_registry_name
  resource_group_name = module.resource_group.name
  location            = module.resource_group.location
  sku                 = "Basic"
  admin_enabled       = false
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

  identity {
    type = "SystemAssigned"
  }

  site_config {
    always_on                               = true
    container_registry_use_managed_identity = true

    application_stack {
      docker_image_name   = "folium-demo:bootstrap"
      docker_registry_url = "https://${azurerm_container_registry.demo[0].login_server}"
    }
  }

  app_settings = {
    WEBSITES_ENABLE_APP_SERVICE_STORAGE = "false"
    WEBSITES_PORT                       = "3000"
  }

  lifecycle {
    ignore_changes = [
      site_config[0].application_stack[0].docker_image_name,
    ]
  }
}

resource "azurerm_role_assignment" "app_service_acr_pull" {
  count = var.enable_app_service_demo ? 1 : 0

  scope                            = azurerm_container_registry.demo[0].id
  role_definition_name             = "AcrPull"
  principal_id                     = azurerm_linux_web_app.container_demo[0].identity[0].principal_id
  skip_service_principal_aad_check = true
}
