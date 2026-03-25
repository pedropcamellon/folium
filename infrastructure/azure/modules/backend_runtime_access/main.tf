data "azurerm_client_config" "current" {}

resource "azurerm_role_assignment" "acr_pull" {
  count                           = var.enable_acr ? 1 : 0
  scope                           = var.acr_id
  role_definition_name            = "AcrPull"
  principal_id                    = var.backend_principal_id
  skip_service_principal_aad_check = true
}

resource "azurerm_role_assignment" "key_vault_secrets_user" {
  count                           = var.enable_key_vault ? 1 : 0
  scope                           = var.key_vault_id
  role_definition_name            = "Key Vault Secrets User"
  principal_id                    = var.backend_principal_id
  skip_service_principal_aad_check = true
}

resource "azurerm_key_vault_access_policy" "backend_container_app" {
  count        = var.enable_key_vault ? 1 : 0
  key_vault_id = var.key_vault_id
  tenant_id    = data.azurerm_client_config.current.tenant_id
  object_id    = var.backend_principal_id

  secret_permissions = [
    "Get",
    "List",
  ]
}