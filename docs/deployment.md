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
