variable "subscription_id" {
  description = "Azure subscription ID for the demo deployment."
  type        = string
  sensitive   = true
}

variable "resource_group_name" {
  description = "Dedicated resource group for the frontend-only demo."
  type        = string
  default     = "rg-folium-demo"
}

variable "location" {
  description = "Azure region for the Static Web App resource."
  type        = string
  default     = "East US 2"
}

variable "static_web_app_name" {
  description = "Globally unique name for the Static Web App."
  type        = string
}
