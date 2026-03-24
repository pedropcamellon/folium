variable "name" {
  type = string
}

variable "location" {
  type = string
}

variable "resource_group_name" {
  type = string
}

variable "sku_name" {
  type = string
}

variable "custom_subdomain_name" {
  type = string
}

variable "deployments" {
  type = map(object({
    name                   = string
    model_format           = string
    model_name             = string
    model_version          = string
    scale_type             = string
    scale_capacity         = number
    version_upgrade_option = string
  }))
}

variable "tags" {
  type = map(string)
}