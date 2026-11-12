locals {
  tags = {
    application = "folium"
    environment = "demo"
    data        = "synthetic"
    managed_by  = "terraform"
  }
}

module "resource_group" {
  source = "../azure/modules/resource_group"

  name     = var.resource_group_name
  location = var.resource_group_location
  tags     = local.tags
}

module "static_web_app" {
  source = "../azure/modules/static_web_app"

  name                = "folium-demo"
  resource_group_name = module.resource_group.name
  location            = var.location
  sku_tier            = "Free"
  sku_size            = "Free"
  tags                = local.tags
}
