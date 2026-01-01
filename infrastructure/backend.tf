# backend.tf - Terraform state configuration

terraform {
  backend "azurerm" {
    resource_group_name  = "terraform-state-rg-dev"
    storage_account_name = "southdrifttfstate"
    container_name       = "tfstate"
    key                  = "south-drift-dev.tfstate"
  }
}