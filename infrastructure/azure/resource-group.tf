# Resource Group

resource "azurerm_resource_group" "south-drift" {
  name     = "rg-south-drift-${var.environment}"
  location = var.location

  tags = {
    environment = var.environment
    project     = "south-drift"
    managed-by  = "terraform"
  }
}
