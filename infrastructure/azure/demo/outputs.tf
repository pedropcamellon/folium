output "resource_group_name" {
  value = module.resource_group.name
}

output "static_web_app_name" {
  value = module.static_web_app.name
}

output "demo_url" {
  value = "https://${module.static_web_app.default_host_name}"
}

output "app_service_demo_url" {
  value = var.enable_app_service_demo ? "https://${azurerm_linux_web_app.container_demo[0].default_hostname}" : null
}

output "container_registry_login_server" {
  value = var.enable_app_service_demo ? azurerm_container_registry.demo[0].login_server : null
}
