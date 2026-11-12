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
  default     = "Central US"
}

variable "resource_group_location" {
  description = "Metadata location of the existing resource group; independent of the hosting region."
  type        = string
  default     = "East US"
}
