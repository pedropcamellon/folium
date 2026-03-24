resource "azurerm_container_app" "this" {
  name                         = var.name
  container_app_environment_id = var.container_app_environment_id
  resource_group_name          = var.resource_group_name
  revision_mode                = "Single"
  tags                         = var.tags

  identity {
    type = "SystemAssigned"
  }

  registry {
    server   = var.acr_login_server
    identity = "System"
  }

  dynamic "secret" {
    for_each = var.key_vault_secret_ids
    content {
      name                = lower(replace(secret.key, "_", "-"))
      identity            = "System"
      key_vault_secret_id = secret.value
    }
  }

  ingress {
    allow_insecure_connections = false
    external_enabled           = true
    target_port                = var.target_port

    traffic_weight {
      latest_revision = true
      percentage      = 100
    }
  }

  template {
    min_replicas = var.min_replicas
    max_replicas = var.max_replicas

    container {
      name   = var.container_name
      image  = var.image
      cpu    = var.cpu
      memory = var.memory

      dynamic "env" {
        for_each = var.environment_variables
        content {
          name  = env.key
          value = env.value
        }
      }

      dynamic "env" {
        for_each = var.key_vault_secret_ids
        content {
          name        = env.key
          secret_name = lower(replace(env.key, "_", "-"))
        }
      }
    }
  }
  
  lifecycle {
    # Terraform bootstraps the app with an initial image. GitHub Actions owns
    # subsequent image updates when it pushes and deploys new revisions.
    ignore_changes = [template[0].container[0].image]
  }
}
