# Folium Deployment Guide

This document outlines the deployment strategy for the Folium application with frontend on Vercel and backend on Azure App Service.

## Architecture Overview

- **Frontend**: Next.js application deployed to Vercel
- **Backend**: ASP.NET Core 8 API deployed to Azure App Service (F1 plan)
- **Infrastructure**: Managed via Terraform
- **CI/CD**: GitHub Actions workflows

## Prerequisites

### Azure Setup

1. Azure subscription with appropriate permissions
2. Service Principal for GitHub Actions authentication
3. Terraform state storage (Resource Group, Storage Account, Container)

What the Script Does
Login and Set Subscription

Ensures you are logged in to Azure and sets the correct subscription context.
Create Resource Group

Creates a resource group (default: rg-terraform-state) in your chosen region (default: East US) to hold the Terraform state storage.
Create Storage Account and Container

Creates a unique storage account (e.g., saterraformstate1234) and a blob container named terraform-state for storing your Terraform state files.
Create Service Principal

Creates an Azure AD service principal for GitHub Actions to use for authentication and deployment.
Assign Contributor Role

Assigns the Contributor role to the service principal at the subscription level so it can manage resources.
Output Credentials and Next Steps

Outputs all the values you need to configure GitHub Actions secrets and the backend block for Terraform.

### Vercel Setup

1. Vercel account connected to your GitHub repository
2. Vercel CLI access token

### GitHub Secrets

Configure the following secrets in your GitHub repository:

#### Azure Secrets

- `AZURE_CREDENTIALS`: Service Principal credentials in JSON format
- `AZURE_SUBSCRIPTION_ID`: Your Azure subscription ID
- `TERRAFORM_STATE_RG`: Resource group for Terraform state storage
- `TERRAFORM_STATE_SA`: Storage account for Terraform state
- `TERRAFORM_STATE_CONTAINER`: Container name for Terraform state

#### Vercel Secrets

- `VERCEL_TOKEN`: Vercel CLI access token
- `VERCEL_ORG_ID`: Your Vercel organization ID
- `VERCEL_PROJECT_ID`: Your Vercel project ID

## Directory Structure

```text
├── .github/workflows/
│   ├── ci.yml                  # Continuous Integration
│   ├── deploy-backend.yml      # Backend deployment to Azure
│   └── deploy-frontend.yml     # Frontend deployment to Vercel
├── infra/
│   ├── main.tf                 # Main Terraform configuration
│   ├── variables.tf            # Input variables
│   ├── outputs.tf              # Output values
│   └── terraform.tfvars.json   # Environment-specific values
├── backend/                    # ASP.NET Core API
└── frontend/                   # Next.js application
    └── vercel.json             # Vercel configuration
```

## Deployment Process

### 1. Initial Setup

1. **Create Azure Service Principal**:

   ```bash
   az ad sp create-for-rbac --name "south-drift-github-actions" --role contributor --scopes /subscriptions/{subscription-id} --sdk-auth
   ```

2. **Setup Terraform State Storage**:

   ```bash
   az group create --name "rg-terraform-state" --location "East US"
   az storage account create --name "saterraformstate{unique}" --resource-group "rg-terraform-state" --location "East US" --sku "Standard_LRS"
   az storage container create --name "terraform-state" --account-name "saterraformstate{unique}"
   ```

3. **Configure Vercel Project**:
   - Connect your GitHub repository to Vercel
   - Get organization and project IDs from Vercel dashboard
   - Generate access token from Vercel settings

### 2. Infrastructure Deployment

The infrastructure is automatically deployed when changes are pushed to the `main` branch affecting the `infra/` or `backend/` directories.

**Manual deployment**:

```bash
cd infra
terraform init
terraform validate
terraform plan -var="environment=dev" -var="subscription_id={your-subscription-id}"
terraform apply
```

### 3. Application Deployment

#### Backend

- Automatically deployed to Azure App Service when changes are pushed to `main`
- Uses F1 (Free) tier App Service plan
- Includes Application Insights for monitoring

#### Frontend

- Automatically deployed to Vercel when changes are pushed to `main`
- Optimized Next.js build with proper environment variables
- Configured for production deployment

## Environment Configuration

### Backend Environment Variables

Configure in Azure App Service application settings:

- `ASPNETCORE_ENVIRONMENT`: Environment name (Development, Staging, Production)
- `APPLICATIONINSIGHTS_CONNECTION_STRING`: Auto-configured by Terraform
- Add your API keys and database connection strings as needed

### Frontend Environment Variables

Configure in Vercel project settings:

- `NEXT_PUBLIC_API_URL`: Backend API URL (auto-set by deployment workflow)

## Monitoring and Troubleshooting

### Azure App Service

- Application Insights provides performance and error monitoring
- Log streaming available through Azure portal
- Health check endpoint: `https://your-app.azurewebsites.net/health`

### Vercel

- Built-in analytics and performance monitoring
- Function logs available in Vercel dashboard
- Real-time deployment logs

## Security Considerations

1. **CORS Configuration**: Backend configured to accept requests from Vercel domains
2. **HTTPS Only**: Both frontend and backend enforce HTTPS
3. **Secrets Management**: Use Azure Key Vault for sensitive data (optional setup included)
4. **Least Privilege**: Service Principal has minimal required permissions

## Cost Optimization

- **Azure App Service F1**: Free tier with limitations (60 minutes/day, no custom domains)
- **Vercel Hobby**: Free tier with generous limits for personal projects
- **Application Insights**: Free tier with 1GB/month data retention

## Scaling Considerations

To scale beyond free tiers:

1. **Azure**: Upgrade to B1 or higher App Service plan
2. **Vercel**: Upgrade to Pro plan for better performance and features
3. **Database**: Consider Azure SQL Database or Cosmos DB for data persistence

## Maintenance

- **Dependencies**: Dependabot configured for automatic updates
- **Security**: Regular security scans via GitHub Security tab
- **Monitoring**: Set up alerts in Application Insights for critical issues
