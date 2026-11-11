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
