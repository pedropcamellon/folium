# Azure Infrastructure

Azure resources for the SouthDrift main application backend.

## Resources

| Resource | Type | Purpose |
|----------|------|---------|
| **Resource Group** | `azurerm_resource_group` | Container for all resources |
| **App Service Plan** | `azurerm_service_plan` | F1 Free tier Linux plan |
| **App Service** | `azurerm_linux_web_app` | ASP.NET Core backend API |
| **Application Insights** | `azurerm_application_insights` | Monitoring and telemetry |
| **Azure OpenAI** | `azurerm_cognitive_account` | GPT-5 Nano for AI services |
| **GPT-5 Deployment** | `azurerm_cognitive_deployment` | GPT-5 Nano model deployment |

## Deployment

### Prerequisites

1. **Azure CLI**: Install and authenticate

   ```powershell
   az login
   az account set --subscription "your-subscription-id"
   ```

2. **Terraform**: Version >= 1.0

   ```powershell
   terraform version
   ```

3. **Storage Account**: For Terraform state (one-time setup)

   ```powershell
   # Create resource group

   az group create --name rg-terraform-state --location "East US"

   # Create storage account
   az storage account create `
     --name southdrifttfstate `
     --resource-group rg-terraform-state `
     --location "East US" `
     --sku Standard_LRS

   # Create container
   az storage container create `
     --name tfstate `
     --account-name southdrifttfstate
   ```

### Deploy

```powershell
# Initialize Terraform
terraform init

# Preview changes
terraform plan

# Deploy infrastructure
terraform apply

# View outputs
terraform output
```

## Configuration

### Required Variables

Set in `terraform.tfvars` or environment variables:

```hcl
environment = "dev"
location = "East US"
subscription_id = "your-azure-subscription-id"
```

### Optional Variables

```hcl
frontend_urls = [
  "http://localhost:3000",
  "https://south-drift.vercel.app"
]

resource_group_name = "custom-rg-name"  # Override default naming
```

## Outputs

| Output | Description |
|--------|-------------|
| `resource_group_name` | Name of the resource group |
| `app_service_name` | Name of the App Service |
| `app_service_hostname` | App Service hostname |
| `app_service_url` | Full HTTPS URL of the backend |
| `application_insights_instrumentation_key` | Application Insights key (sensitive) |
| `application_insights_connection_string` | Connection string (sensitive) |
| `openai_endpoint` | Azure OpenAI endpoint URL |
| `openai_api_key` | Azure OpenAI API key (sensitive) |
| `openai_deployment_name` | GPT-5 Nano deployment name |
| `docker_compose_config` | Complete config for docker-compose (sensitive) |

### Retrieve Outputs

```powershell
# All outputs
terraform output

# Specific output

# Azure OpenAI configuration for Docker
terraform output -json docker_compose_config
```

## Azure OpenAI Configuration

### GPT-5 Nano

**Model**: `gpt-5-nano` (Version: 2025-08-07)

- **Speed**: Very fast (1-2s)
- **Cost**: $0.14 per 1M tokens
- **Quality**: 0.83 quality index
- **Use Case**: High-volume, cost-efficient summaries

**Environment Variables**:

```bash
AZURE_OPENAI_ENDPOINT=https://cog-south-drift-openai-dev.openai.azure.com/
AZURE_OPENAI_KEY=<from_terraform_output>
AZURE_OPENAI_DEPLOYMENT=gpt-5-nano
AZURE_OPENAI_API_VERSION=2024-02-15-preview
```

**Get Credentials**:

```powershell
# Extract all config
terraform output -json docker_compose_config > azure-openai-config.json

# Or individual values
terraform output openai_endpoint
terraform output -raw openai_api_key
terraform output app_service_url

# Sensitive output
terraform output -raw application_insights_instrumentation_key
```

## App Service Configuration

### Environment Variables

Set in Azure Portal or via CLI:

```powershell
az webapp config appsettings set `
  --name app-south-drift-backend-dev `
  --resource-group rg-south-drift-dev `
  --settings `
    ASPNETCORE_ENVIRONMENT=Production `
    APPLICATIONINSIGHTS_CONNECTION_STRING="$(terraform output -raw application_insights_connection_string)" `
    SUMMARIZATION_SERVICE_URL="http://summarize:8002"
```

### Deployment

**Option 1: Docker Container (Recommended)**

```powershell
# Build and push to Azure Container Registry
az acr build `
  --registry southdriftacr `
  --image backend:latest `
  --file backend/Dockerfile `
  .

# Configure App Service to use container
az webapp config container set `
  --name app-south-drift-backend-dev `
  --resource-group rg-south-drift-dev `
  --docker-custom-image-name southdriftacr.azurecr.io/backend:latest
```

**Option 2: GitHub Actions (CI/CD)**

See `.github/workflows/deploy-azure-backend.yml`

## Monitoring

### Application Insights

**View Logs**:

```powershell
az monitor app-insights query `
  --app $(terraform output -raw app_service_name) `
  --analytics-query "traces | where timestamp > ago(1h) | order by timestamp desc"
```

**View Metrics**:

- Azure Portal → Application Insights → Metrics
- Select: Requests, Response time, Failed requests

**Alerts**:

- High error rate (>5% failed requests)
- Slow response time (>2s p95)
- High CPU/memory usage

## Scaling

### Upgrade App Service Plan

```powershell
# Change from F1 (Free) to B1 (Basic)
az appservice plan update `
  --name asp-south-drift-dev `
  --resource-group rg-south-drift-dev `
  --sku B1
```

### Auto-scaling (Premium tier required)

```powershell
# Enable auto-scaling
az monitor autoscale create `
  --resource-group rg-south-drift-dev `
  --resource asp-south-drift-dev `
  --resource-type Microsoft.Web/serverfarms `
  --name autoscale-south-drift `
  --min-count 1 `
  --max-count 3 `
  --count 1

# Add CPU rule
az monitor autoscale rule create `
  --resource-group rg-south-drift-dev `
  --autoscale-name autoscale-south-drift `
  --condition "Percentage CPU > 70 avg 5m" `
  --scale out 1
```

## Troubleshooting

### "State file locked"

Another user or process is modifying the state.

```powershell
# List locks
az lock list --resource-group rg-south-drift-dev

# Force unlock (use carefully)
terraform force-unlock <lock-id>
```

### "Insufficient permissions"

Verify your Azure account has the required roles:

```powershell
# Check current account
az account show

# Assign Contributor role (if needed)
az role assignment create `
  --assignee "your-email@example.com" `
  --role Contributor `
  --scope /subscriptions/your-subscription-id
```

### App Service not starting

```powershell
# View logs
az webapp log tail `
  --name app-south-drift-backend-dev `
  --resource-group rg-south-drift-dev

# Check configuration
az webapp config show `
  --name app-south-drift-backend-dev `
  --resource-group rg-south-drift-dev
```

## Cleanup

```powershell
# Destroy all resources
terraform destroy

# Or delete resource group manually
az group delete --name rg-south-drift-dev --yes
```

## Cost Optimization

| Tier | Monthly Cost | Use Case |
|------|--------------|----------|
| **F1 Free** | $0 | Development, testing |
| **B1 Basic** | ~$13 | Staging, low traffic |
| **S1 Standard** | ~$70 | Production, moderate traffic |
| **P1v2 Premium** | ~$150 | Production, high traffic, auto-scaling |

**Tips**:

- Use F1 for development (60 CPU minutes/day limit)
- Schedule App Service to turn off during non-business hours
- Use Azure Cost Management for tracking
- Set budget alerts at 80% and 100%

---
**Last Updated**: 2026-01-02  
**Azure Subscription**: Visual Studio Enterprise
