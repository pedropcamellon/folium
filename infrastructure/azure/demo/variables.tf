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
  description = "Azure region for the frontend demo resources."
  type        = string
  default     = "East US 2"
}

variable "enable_app_service_demo" {
  description = "Create Free F1 App Service using the built-in Node runtime."
  type        = bool
  default     = false
}

variable "app_service_plan_name" {
  description = "Name of the Linux F1 App Service plan."
  type        = string
  default     = "asp-folium-demo-free"
}

variable "app_service_name" {
  description = "Globally unique name of the Node demo Web App."
  type        = string
  default     = "folium-demo-free"
}
