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

variable "static_web_app_name" {
  description = "Globally unique name for the Static Web App."
  type        = string
}

variable "enable_app_service_demo" {
  description = "Create the paid Linux B1 App Service container environment."
  type        = bool
  default     = false
}

variable "app_service_plan_name" {
  description = "Name of the Linux B1 App Service plan."
  type        = string
  default     = "asp-folium-demo-container"
}

variable "app_service_name" {
  description = "Globally unique name of the container-based demo Web App."
  type        = string
  default     = "folium-demo-container"
}

variable "container_image" {
  description = "Public GHCR image and tag used by the container-based demo."
  type        = string
  default     = "ghcr.io/pedropcamellon/folium-demo:latest"
}
