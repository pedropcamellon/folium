# PowerShell script to set up Azure resources for deployment

param(
    [Parameter(Mandatory = $true)]
    [string]$SubscriptionId,
    
    [Parameter(Mandatory = $false)]
    [string]$ResourceGroupName = "rg-terraform-state",
    
    [Parameter(Mandatory = $false)]
    [string]$Location = "East US",
    
    [Parameter(Mandatory = $false)]
    [string]$StorageAccountPrefix = "saterraformstate"
)

Write-Host "Setting up Azure resources for deployment..." -ForegroundColor Green

# Login to Azure (if not already logged in)
$context = Get-AzContext
if (-not $context) {
    Write-Host "Please login to Azure..." -ForegroundColor Yellow
    Connect-AzAccount
}

# Set subscription
Write-Host "Setting subscription to: $SubscriptionId" -ForegroundColor Yellow
Set-AzContext -SubscriptionId $SubscriptionId

# Generate unique storage account name
$randomSuffix = Get-Random -Minimum 1000 -Maximum 9999
$storageAccountName = "$StorageAccountPrefix$randomSuffix"

# Create resource group for Terraform state
Write-Host "Creating resource group: $ResourceGroupName" -ForegroundColor Yellow
$rg = New-AzResourceGroup -Name $ResourceGroupName -Location $Location -Force

# Create storage account for Terraform state
Write-Host "Creating storage account: $storageAccountName" -ForegroundColor Yellow
$storageAccount = New-AzStorageAccount `
    -ResourceGroupName $ResourceGroupName `
    -Name $storageAccountName `
    -Location $Location `
    -SkuName "Standard_LRS" `
    -Kind "StorageV2"

# Create container for Terraform state
Write-Host "Creating storage container: terraform-state" -ForegroundColor Yellow
$ctx = $storageAccount.Context
$container = New-AzStorageContainer -Name "terraform-state" -Context $ctx -Permission Off

# Create service principal for GitHub Actions
Write-Host "Creating service principal for GitHub Actions..." -ForegroundColor Yellow
$spName = "sp-south-drift-github-actions"
$sp = New-AzADServicePrincipal -DisplayName $spName

# Assign Contributor role to service principal
Write-Host "Assigning Contributor role to service principal..." -ForegroundColor Yellow
Start-Sleep -Seconds 30  # Wait for service principal to propagate
New-AzRoleAssignment -ObjectId $sp.Id -RoleDefinitionName "Contributor" -Scope "/subscriptions/$SubscriptionId"

# Generate service principal credentials JSON for GitHub Actions
$credentials = @{
    clientId                       = $sp.AppId
    clientSecret                   = [System.Runtime.InteropServices.Marshal]::PtrToStringAuto([System.Runtime.InteropServices.Marshal]::SecureStringToBSTR($sp.PasswordCredentials.SecretText))
    subscriptionId                 = $SubscriptionId
    tenantId                       = (Get-AzContext).Tenant.Id
    activeDirectoryEndpointUrl     = "https://login.microsoftonline.com"
    resourceManagerEndpointUrl     = "https://management.azure.com/"
    activeDirectoryGraphResourceId = "https://graph.windows.net/"
    sqlManagementEndpointUrl       = "https://management.core.windows.net:8443/"
    galleryEndpointUrl             = "https://gallery.azure.com/"
    managementEndpointUrl          = "https://management.core.windows.net/"
}

$credentialsJson = $credentials | ConvertTo-Json -Compress

Write-Host "`n================================" -ForegroundColor Green
Write-Host "SETUP COMPLETED SUCCESSFULLY!" -ForegroundColor Green
Write-Host "================================" -ForegroundColor Green

Write-Host "`nGitHub Secrets Configuration:" -ForegroundColor Cyan
Write-Host "Add the following secrets to your GitHub repository:" -ForegroundColor Yellow

Write-Host "`nAZURE_CREDENTIALS:" -ForegroundColor White
Write-Host $credentialsJson -ForegroundColor Gray

Write-Host "`nAZURE_SUBSCRIPTION_ID:" -ForegroundColor White
Write-Host $SubscriptionId -ForegroundColor Gray

Write-Host "`nTERRAFORM_STATE_RG:" -ForegroundColor White
Write-Host $ResourceGroupName -ForegroundColor Gray

Write-Host "`nTERRAFORM_STATE_SA:" -ForegroundColor White
Write-Host $storageAccountName -ForegroundColor Gray

Write-Host "`nTERRAFORM_STATE_CONTAINER:" -ForegroundColor White
Write-Host "terraform-state" -ForegroundColor Gray

Write-Host "`nNext Steps:" -ForegroundColor Cyan
Write-Host "1. Add the above secrets to your GitHub repository settings" -ForegroundColor Yellow
Write-Host "2. Update the Terraform backend configuration in infra/backend.tf" -ForegroundColor Yellow
Write-Host "3. Set up Vercel project and add Vercel secrets to GitHub" -ForegroundColor Yellow
Write-Host "4. Push your code to trigger the deployment workflows" -ForegroundColor Yellow

Write-Host "`nTerraform Backend Configuration:" -ForegroundColor Cyan
Write-Host "Update infra/backend.tf with:" -ForegroundColor Yellow
Write-Host @"
terraform {
  backend "azurerm" {
    resource_group_name  = "$ResourceGroupName"
    storage_account_name = "$storageAccountName"
    container_name       = "terraform-state"
    key                  = "south-drift-dev.tfstate"
  }
}
"@ -ForegroundColor Gray
