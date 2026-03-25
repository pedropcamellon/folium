output "vnet_id" {
  value = var.enabled ? azurerm_virtual_network.this[0].id : null
}

output "vnet_name" {
  value = var.enabled ? azurerm_virtual_network.this[0].name : null
}

output "container_apps_subnet_id" {
  value = var.enabled ? azurerm_subnet.container_apps[0].id : null
}

output "postgres_subnet_id" {
  value = var.enabled ? azurerm_subnet.postgres[0].id : null
}
