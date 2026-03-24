# Input variables for the Terraform configuration

variable "environment" {
  description = "Environment name (dev, staging, prod)"
  type        = string
  default     = "dev"

  validation {
    condition     = can(regex("^(dev|staging|prod)$", var.environment))
    error_message = "Environment must be one of: dev, staging, prod."
  }
}

variable "location" {
  description = "Azure region for all resources"
  type        = string
  default     = "East US"
}

variable "deployment_config" {
  description = "Config-driven deployment object for Azure infrastructure modules"
  type = object({
    naming = optional(object({
      prefix = optional(string)
    }))
    features = optional(object({
      network               = optional(bool)
      acr                   = optional(bool)
      monitoring            = optional(bool)
      key_vault             = optional(bool)
      postgres              = optional(bool)
      container_apps_env    = optional(bool)
      backend_container_app = optional(bool)
      static_web_app        = optional(bool)
      openai                = optional(bool)
    }))
    network = optional(object({
      address_space              = optional(list(string))
      container_apps_subnet_cidr = optional(string)
      postgres_subnet_cidr       = optional(string)
    }))
    acr = optional(object({
      sku = optional(string)
    }))
    monitoring = optional(object({
      retention_in_days = optional(number)
      daily_quota_gb    = optional(number)
    }))
    key_vault = optional(object({
      sku_name                   = optional(string)
      soft_delete_retention_days = optional(number)
    }))
    postgres = optional(object({
      version                       = optional(string)
      administrator_login           = optional(string)
      sku_name                      = optional(string)
      storage_mb                    = optional(number)
      backup_retention_days         = optional(number)
      zone                          = optional(string)
      public_network_access_enabled = optional(bool)
      database_name                 = optional(string)
    }))
    container_apps = optional(object({
      target_port  = optional(number)
      min_replicas = optional(number)
      max_replicas = optional(number)
      cpu          = optional(number)
      memory       = optional(string)
      image        = optional(string)
    }))
    static_web_app = optional(object({
      sku_tier = optional(string)
      sku_size = optional(string)
    }))
    openai = optional(object({
      sku_name              = optional(string)
      custom_subdomain_name = optional(string)
      deployments = optional(map(object({
        name                   = string
        model_format           = string
        model_name             = string
        model_version          = string
        scale_type             = string
        scale_capacity         = number
        version_upgrade_option = string
      })))
    }))
    tags = optional(map(string))
  })
  default = {}
}

variable "subscription_id" {
  description = "Azure subscription ID"
  type        = string
  sensitive   = true
}
