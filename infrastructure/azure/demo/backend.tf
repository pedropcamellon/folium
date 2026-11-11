terraform {
  backend "azurerm" {
    resource_group_name  = "rg-terraform-state"
    storage_account_name = "southdrifttfstate"
    container_name       = "tfstate"
    key                  = "folium-demo-static-web-app.tfstate"
    use_azuread_auth     = true
    use_cli              = true
  }
}
