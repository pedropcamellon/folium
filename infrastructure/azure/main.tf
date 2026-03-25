locals {
  base_tags = {
    environment = var.environment
    project     = "south-drift"
    managed-by  = "terraform"
  }

  default_config = {
    naming = {
      prefix = "southdrift"
    }
    features = {
      network               = false
      acr                   = true
      monitoring            = true
      key_vault             = true
      postgres              = true
      container_apps_env    = true
      backend_container_app = true
      static_web_app        = true
      openai                = true
    }
    network = {
      address_space              = ["10.40.0.0/16"]
      container_apps_subnet_cidr = "10.40.0.0/23"
      postgres_subnet_cidr       = "10.40.2.0/28"
    }
    acr = {
      sku = "Basic"
    }
    monitoring = {
      retention_in_days = 30
      daily_quota_gb    = 1
    }
    key_vault = {
      sku_name                   = "standard"
      soft_delete_retention_days = 7
    }
    postgres = {
      version                       = "16"
      administrator_login           = "southdriftadmin"
      sku_name                      = "B_Standard_B1ms"
      storage_mb                    = 32768
      backup_retention_days         = 7
      zone                          = "1"
      public_network_access_enabled = true
      database_name                 = "southdrift_db"
    }
    container_apps = {
      target_port  = 8000
      min_replicas = 0
      max_replicas = 1
      cpu          = 0.25
      memory       = "0.5Gi"
      # Bootstrap image so Terraform can create the Container App before CI/CD
      # publishes the real backend image to ACR.
      image = "mcr.microsoft.com/azuredocs/containerapps-helloworld:latest"
    }
    static_web_app = {
      sku_tier = "Free"
      sku_size = "Free"
    }
    openai = {
      sku_name              = "S0"
      custom_subdomain_name = format("southdrift-openai-%s", var.environment)
      deployments = {
        gpt5_nano = {
          name                   = "gpt-5-nano"
          model_format           = "OpenAI"
          model_name             = "gpt-5-nano"
          model_version          = "2025-08-07"
          scale_type             = "GlobalStandard"
          scale_capacity         = 200
          version_upgrade_option = "OnceCurrentVersionExpired"
        }
        gpt41_nano = {
          name                   = "gpt-4.1-nano"
          model_format           = "OpenAI"
          model_name             = "gpt-4.1-nano"
          model_version          = "2025-04-14"
          scale_type             = "GlobalStandard"
          scale_capacity         = 200
          version_upgrade_option = "OnceCurrentVersionExpired"
        }
      }
    }
  }

  config = {
    naming         = merge(local.default_config.naming, try(var.deployment_config.naming, {}))
    features       = merge(local.default_config.features, try(var.deployment_config.features, {}))
    network        = merge(local.default_config.network, try(var.deployment_config.network, {}))
    acr            = merge(local.default_config.acr, try(var.deployment_config.acr, {}))
    monitoring     = merge(local.default_config.monitoring, try(var.deployment_config.monitoring, {}))
    key_vault      = merge(local.default_config.key_vault, try(var.deployment_config.key_vault, {}))
    postgres       = merge(local.default_config.postgres, try(var.deployment_config.postgres, {}))
    container_apps = merge(local.default_config.container_apps, try(var.deployment_config.container_apps, {}))
    static_web_app = merge(local.default_config.static_web_app, try(var.deployment_config.static_web_app, {}))
    openai         = merge(local.default_config.openai, try(var.deployment_config.openai, {}))
    tags           = merge(local.base_tags, try(var.deployment_config.tags, {}))
  }

  resource_group_name        = format("rg-%s-%s", local.config.naming.prefix, var.environment)
  vnet_name                  = format("vnet-%s-%s", local.config.naming.prefix, var.environment)
  container_registry_name    = substr(replace(lower(format("%s%sacr", local.config.naming.prefix, var.environment)), "-", ""), 0, 50)
  key_vault_name             = substr(lower(format("kv-%s-%s", local.config.naming.prefix, var.environment)), 0, 24)
  log_analytics_name         = format("log-%s-%s", local.config.naming.prefix, var.environment)
  application_insights_name  = format("appi-%s-%s", local.config.naming.prefix, var.environment)
  container_apps_environment = format("cae-%s-%s", local.config.naming.prefix, var.environment)
  backend_container_app_name = format("ca-%s-backend-%s", local.config.naming.prefix, var.environment)
  static_web_app_name        = format("swa-%s-%s", local.config.naming.prefix, var.environment)
  postgres_server_name       = substr(replace(lower(format("psql-%s-%s", local.config.naming.prefix, var.environment)), "-", ""), 0, 63)
  openai_account_name        = format("%s-aiservices-%s", local.config.naming.prefix, var.environment)
  backend_image              = local.config.container_apps.image
}

module "resource_group" {
  source   = "./modules/resource_group"
  name     = local.resource_group_name
  location = var.location
  tags     = local.config.tags
}

module "network" {
  source                     = "./modules/network"
  enabled                    = local.config.features.network
  name                       = local.vnet_name
  location                   = module.resource_group.location
  resource_group_name        = module.resource_group.name
  address_space              = local.config.network.address_space
  container_apps_subnet_cidr = local.config.network.container_apps_subnet_cidr
  postgres_subnet_cidr       = local.config.network.postgres_subnet_cidr
  tags                       = local.config.tags
}

module "acr" {
  count               = local.config.features.acr ? 1 : 0
  source              = "./modules/acr"
  name                = local.container_registry_name
  location            = module.resource_group.location
  resource_group_name = module.resource_group.name
  sku                 = local.config.acr.sku
  tags                = local.config.tags
}

module "monitoring" {
  count                     = local.config.features.monitoring ? 1 : 0
  source                    = "./modules/monitoring"
  workspace_name            = local.log_analytics_name
  application_insights_name = local.application_insights_name
  location                  = module.resource_group.location
  resource_group_name       = module.resource_group.name
  retention_in_days         = local.config.monitoring.retention_in_days
  daily_quota_gb            = local.config.monitoring.daily_quota_gb
  tags                      = local.config.tags
}

module "key_vault" {
  count                      = local.config.features.key_vault ? 1 : 0
  source                     = "./modules/key_vault"
  name                       = local.key_vault_name
  location                   = module.resource_group.location
  resource_group_name        = module.resource_group.name
  sku_name                   = local.config.key_vault.sku_name
  soft_delete_retention_days = local.config.key_vault.soft_delete_retention_days
  tags                       = local.config.tags
}

module "postgres" {
  count                         = local.config.features.postgres ? 1 : 0
  source                        = "./modules/postgres_flexible"
  server_name                   = local.postgres_server_name
  database_name                 = local.config.postgres.database_name
  location                      = module.resource_group.location
  resource_group_name           = module.resource_group.name
  postgres_version              = local.config.postgres.version
  administrator_login           = coalesce(local.config.postgres.administrator_login, local.default_config.postgres.administrator_login)
  sku_name                      = local.config.postgres.sku_name
  storage_mb                    = local.config.postgres.storage_mb
  backup_retention_days         = local.config.postgres.backup_retention_days
  zone                          = local.config.postgres.zone
  public_network_access_enabled = local.config.postgres.public_network_access_enabled
  delegated_subnet_id           = local.config.features.network ? module.network.postgres_subnet_id : null
  tags                          = local.config.tags
}

module "container_apps_env" {
  count                      = local.config.features.container_apps_env && local.config.features.monitoring ? 1 : 0
  source                     = "./modules/container_apps_env"
  name                       = local.container_apps_environment
  location                   = module.resource_group.location
  resource_group_name        = module.resource_group.name
  log_analytics_workspace_id = module.monitoring[0].log_analytics_workspace_id
  infrastructure_subnet_id   = local.config.features.network ? module.network.container_apps_subnet_id : null
  tags                       = local.config.tags
}

module "static_web_app" {
  count               = local.config.features.static_web_app ? 1 : 0
  source              = "./modules/static_web_app"
  name                = local.static_web_app_name
  location            = module.resource_group.location
  resource_group_name = module.resource_group.name
  sku_tier            = local.config.static_web_app.sku_tier
  sku_size            = local.config.static_web_app.sku_size
  tags                = local.config.tags
}

module "openai" {
  count                 = local.config.features.openai ? 1 : 0
  source                = "./modules/openai"
  name                  = local.openai_account_name
  location              = module.resource_group.location
  resource_group_name   = module.resource_group.name
  sku_name              = local.config.openai.sku_name
  custom_subdomain_name = local.config.openai.custom_subdomain_name
  deployments           = local.config.openai.deployments
  tags                  = local.config.tags
}

resource "azurerm_key_vault_secret" "postgres_admin_password" {
  count        = local.config.features.key_vault && local.config.features.postgres ? 1 : 0
  name         = "postgres-admin-password"
  value        = module.postgres[0].administrator_password
  key_vault_id = module.key_vault[0].id

  depends_on = [module.key_vault]
}

resource "azurerm_key_vault_secret" "database_url" {
  count        = local.config.features.key_vault && local.config.features.postgres ? 1 : 0
  name         = "database-url"
  value        = format("postgresql+asyncpg://%s:%s@%s/%s", coalesce(local.config.postgres.administrator_login, local.default_config.postgres.administrator_login), module.postgres[0].administrator_password, module.postgres[0].fqdn, module.postgres[0].database_name)
  key_vault_id = module.key_vault[0].id

  depends_on = [module.key_vault]
}

resource "azurerm_key_vault_secret" "application_insights_connection_string" {
  count        = local.config.features.key_vault && local.config.features.monitoring ? 1 : 0
  name         = "application-insights-connection-string"
  value        = module.monitoring[0].application_insights_connection_string
  key_vault_id = module.key_vault[0].id

  depends_on = [module.key_vault]
}

module "backend_container_app" {
  count                        = local.config.features.backend_container_app && local.config.features.acr && local.config.features.container_apps_env ? 1 : 0
  source                       = "./modules/backend_container_app"
  name                         = local.backend_container_app_name
  resource_group_name          = module.resource_group.name
  container_app_environment_id = module.container_apps_env[0].id
  acr_login_server             = module.acr[0].login_server
  image                        = local.backend_image
  target_port                  = local.config.container_apps.target_port
  min_replicas                 = local.config.container_apps.min_replicas
  max_replicas                 = local.config.container_apps.max_replicas
  cpu                          = local.config.container_apps.cpu
  memory                       = local.config.container_apps.memory
  environment_variables = {
    APP_ENV = var.environment
  }
  key_vault_secret_ids = local.config.features.key_vault && local.config.features.postgres && local.config.features.monitoring ? {
    DATABASE_URL                          = azurerm_key_vault_secret.database_url[0].id
    APPLICATIONINSIGHTS_CONNECTION_STRING = azurerm_key_vault_secret.application_insights_connection_string[0].id
  } : {}
  tags = local.config.tags
}

resource "azurerm_role_assignment" "backend_acr_pull" {
  count                            = local.config.features.backend_container_app && local.config.features.acr ? 1 : 0
  scope                            = module.acr[0].id
  role_definition_name             = "AcrPull"
  principal_id                     = module.backend_container_app[0].principal_id
  skip_service_principal_aad_check = true
}

resource "azurerm_role_assignment" "backend_key_vault_secrets_user" {
  count                            = local.config.features.backend_container_app && local.config.features.key_vault ? 1 : 0
  scope                            = module.key_vault[0].id
  role_definition_name             = "Key Vault Secrets User"
  principal_id                     = module.backend_container_app[0].principal_id
  skip_service_principal_aad_check = true
}

resource "azurerm_key_vault_access_policy" "backend_container_app" {
  count        = local.config.features.backend_container_app && local.config.features.key_vault ? 1 : 0
  key_vault_id = module.key_vault[0].id
  tenant_id    = data.azurerm_client_config.current.tenant_id
  object_id    = module.backend_container_app[0].principal_id

  secret_permissions = [
    "Get",
    "List",
  ]
}
