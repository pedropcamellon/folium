# Azure OpenAI Service

# Azure AI Services (OpenAI)
resource "azurerm_ai_services" "openai" {
  name                = "southdrift-aiservices-${var.environment}"
  location            = azurerm_resource_group.south-drift.location
  resource_group_name = azurerm_resource_group.south-drift.name
  sku_name            = "S0"

  custom_subdomain_name = "southdrift-openai-${var.environment}"

  identity {
    type = "SystemAssigned"
  }

  tags = {
    environment = var.environment
    project     = "south-drift"
    managed-by  = "terraform"
  }
}

# GPT-5 Nano Deployment
resource "azurerm_cognitive_deployment" "gpt5_nano" {
  name                 = "gpt-5-nano"
  cognitive_account_id = azurerm_ai_services.openai.id

  model {
    format  = "OpenAI"
    name    = "gpt-5-nano"
    version = "2025-08-07"
  }

  scale {
    type     = "GlobalStandard"
    capacity = 200
  }

  version_upgrade_option = "OnceCurrentVersionExpired"
}


# GPT-4.1 Nano Deployment (Real Azure OpenAI Model)
resource "azurerm_cognitive_deployment" "gpt41_nano" {
  name                 = "gpt-4.1-nano"
  cognitive_account_id = azurerm_ai_services.openai.id

  model {
    format  = "OpenAI"
    name    = "gpt-4.1-nano"
    version = "2025-04-14"
  }

  scale {
    type     = "GlobalStandard"
    capacity = 200
  }

  version_upgrade_option = "OnceCurrentVersionExpired"
}
