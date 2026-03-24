resource "random_password" "postgres_admin" {
  length           = 24
  special          = false
}

resource "azurerm_postgresql_flexible_server" "this" {
  name                   = var.server_name
  resource_group_name    = var.resource_group_name
  location               = var.location
  version                = var.postgres_version
  delegated_subnet_id    = var.delegated_subnet_id
  administrator_login    = var.administrator_login
  administrator_password = coalesce(var.administrator_password, random_password.postgres_admin.result)
  zone                   = var.zone
  storage_mb             = var.storage_mb
  sku_name               = var.sku_name
  backup_retention_days  = var.backup_retention_days
  public_network_access_enabled = var.public_network_access_enabled
  tags                   = var.tags
}

resource "azurerm_postgresql_flexible_server_database" "this" {
  name      = var.database_name
  server_id = azurerm_postgresql_flexible_server.this.id
  charset   = "UTF8"
  collation = "en_US.utf8"
}
