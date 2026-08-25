terraform {
  backend "azurerm" {
    resource_group_name  = "rg-terraform-state"
    storage_account_name = "foliumtfstate"
    container_name       = "tfstate"
    key                  = "south-drift-dev.tfstate"
  }
}