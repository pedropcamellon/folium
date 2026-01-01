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

variable "frontend_urls" {
  description = "List of frontend URLs for CORS configuration"
  type        = list(string)
  default = [
    "http://localhost:3000",
    "https://localhost:3000",
    "https://*.vercel.app"
  ]
}

variable "subscription_id" {
  description = "Azure subscription ID"
  type        = string
  sensitive   = true
}

variable "resource_group_name" {
  description = "Override default resource group name"
  type        = string
  default     = ""
}
