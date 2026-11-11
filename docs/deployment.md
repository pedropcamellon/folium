# Deployment Guide

## Azure Static Web Apps demo

The public frontend demo is deployed independently from the full-stack Azure
environment. It uses synthetic data in mock mode and does not require a
backend, database, or model-serving resources.

Production demo URL (updated by GitHub Actions after each successful `main`
deployment):

<!-- demo-url:start -->
Pending first successful deployment.
<!-- demo-url:end -->

The GitHub Actions workflow deploys pushes to `main` and creates pull-request
preview deployments. It sets `NEXT_PUBLIC_API_MODE=mock`. URL-only commits to
this guide do not retrigger deployment.

## Provisioning

Terraform in `infrastructure/azure/demo/` reuses the Azure resource-group and
Static Web Apps modules. It creates only a dedicated resource group and a
Free-tier Static Web App. Do not apply `infrastructure/azure/`, which
provisions the full-stack application and paid services.

The demo state uses the dedicated `foliumdemotfstate` storage account and the
separate `folium-demo-static-web-app.tfstate` key in the `tfstate` container.
Azure CLI authentication is used for state access. The signed-in identity
needs the **Storage Blob Data Contributor** role on the state container.

Authenticate with Azure CLI, then provision the isolated demo target:

```bash
cd infrastructure/azure/demo
terraform init
terraform apply \
  -var="subscription_id=$(az account show --query id --output tsv)" \
  -var="static_web_app_name=<globally-unique-name>"
```

The default resource group is `rg-folium-demo` in `East US 2`. The app name
must be globally unique. Terraform tags resources with the application,
environment, synthetic-data, and management metadata.

## GitHub Actions Terraform plan and apply

`.github/workflows/terraform-azure-demo.yml` validates Terraform on pull
requests. Plan and apply run only through manual dispatch on `main`; apply
requires `confirm_apply=true`. The job targets the `azure-demo` GitHub
Environment; configure that Environment to require reviewer approval before
dispatching applies.

Configure these Environment variables in GitHub:

- `AZURE_CLIENT_ID`, `AZURE_TENANT_ID`, and `AZURE_SUBSCRIPTION_ID` for an
  Azure identity with a federated credential for
  `repo:pedropcamellon/folium:environment:azure-demo`.
- `AZURE_DEMO_STATIC_WEB_APP_NAME` for the globally unique app name.

Grant that identity **Storage Blob Data Contributor** on the
`foliumdemotfstate/tfstate` container and **Contributor** only on
`rg-folium-demo`. For the first run, create the resource group with an
authorized operator identity and import it into the demo state before using
the GitHub workflow; do not grant the workflow subscription-wide Contributor
just to create the group.

```bash
az group create --name rg-folium-demo --location "East US 2"
cd infrastructure/azure/demo
terraform init
terraform import \
  -var="subscription_id=$(az account show --query id --output tsv)" \
  -var="static_web_app_name=<globally-unique-name>" \
  module.resource_group.azurerm_resource_group.this \
  "/subscriptions/$(az account show --query id --output tsv)/resourceGroups/rg-folium-demo"
```

In the `azure-demo` Environment settings, require reviewer approval for
deployments. Configure the Azure app registration's federated credential with
issuer `https://token.actions.githubusercontent.com` and audience
`api://AzureADTokenExchange`; no client secret is needed.

Set the GitHub Actions deployment token without printing its value:

```bash
az staticwebapp secrets list --name <app-name> --resource-group rg-folium-demo \
  --query properties.apiKey --output tsv |
  gh secret set AZURE_STATIC_WEB_APPS_API_TOKEN
```

The Free tier has service limits; exceeding them may require a plan change.
No backend, database, registry, monitoring, secrets vault, or model service is
part of this target.

## Teardown

Remove only the dedicated demo target:

```bash
cd infrastructure/azure/demo
terraform destroy \
  -var="subscription_id=$(az account show --query id --output tsv)" \
  -var="static_web_app_name=<globally-unique-name>"
```

## Safety and limitations

The demo is for product demonstration and development only. It is not a
clinical system and must not be used with real patient information. Mock data
is synthetic and held in memory; changes do not persist. Mock mode does not
provide production authentication, persistence, or clinical decision support.

See the [local runtime guide](dev/local-development.md) for running the
complete application stack.
