output "resource_group_name" {
  value = module.resource_group.name
}

output "demo_url" {
  value = var.enable_app_service_demo ? "https://${azurerm_linux_web_app.container_demo[0].default_hostname}" : null
}
