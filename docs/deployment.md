# Deployment Guide

## Azure mock frontend demo

The public frontend demo is deployed independently from the full-stack Azure
environment. It uses synthetic data in mock mode and does not require a
backend, database, or model-serving resources.

Production demo URL (updated by GitHub Actions after each successful `main`
deployment and HTTP smoke test):

<!-- demo-url:start -->
Pending first successful deployment.
<!-- demo-url:end -->

The current deployment remains on Azure Static Web Apps until the App Service
container migration is provisioned and enabled. The container workflow builds
and smoke-tests the production image on frontend changes, publishes the tested
image to Azure Container Registry on `main`, and deploys its immutable digest
only when `AZURE_DEMO_APPSERVICE_ENABLED=true` is configured in the
`azure-demo` Environment. It updates this URL only after the deployed endpoint
passes an HTTP smoke test. URL-only commits to this guide do not retrigger
deployment.

GitHub Actions uses Azure OIDC with AcrPush permission; the Web App pulls
from the private registry using its system-assigned identity with AcrPull.
Registry admin credentials remain disabled. Configure the `azure-demo`
Environment with its Azure OIDC variables, ACR name, and reviewer protection.

## Provisioning

Terraform in `infrastructure/azure/demo/` reuses the Azure resource-group and
Static Web Apps modules. By default, it creates only a dedicated resource
group and a Free-tier Static Web App. The optional App Service container
resources use a Linux B1 plan and incur recurring charges. Enable them only
after reviewing current pricing and authorizing the cost. Do not apply
`infrastructure/azure/`, which provisions the full-stack application and
other paid services.

The optional container target also provisions a private Basic Azure Container
Registry. Current published list pricing is $0.167/day for ACR Basic (about
$5.09/month at 30.4 days); Linux B1 was previously estimated at $12.41/month
for 730 hours in East US 2. The combined estimate is about $17.50/month before
taxes, billing adjustments, storage overages, and network costs. Recheck
current prices before provisioning.

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
  -var="static_web_app_name=<globally-unique-name>" \
  -var="container_registry_name=<globally-unique-name>"
```

The default resource group is `rg-folium-demo` in `East US 2`. The app name
must be globally unique. Terraform tags resources with the application,
environment, synthetic-data, and management metadata. To include the paid
container resources, explicitly set `-var="enable_app_service_demo=true"` and
review the Terraform plan before applying.

## GitHub Actions Terraform plan and apply

`.github/workflows/terraform-azure-demo.yml` validates Terraform on pull
requests. Plan and apply run only through manual dispatch on `main`; apply
requires `confirm_apply=true`. The job targets the `azure-demo` GitHub
Environment; configure that Environment to require reviewer approval before
dispatching applies.

Configure these Environment variables in GitHub:

- `AZURE_CLIENT_ID`, `AZURE_TENANT_ID`, and `AZURE_SUBSCRIPTION_ID` for an
  Azure identity with a federated credential for
  `repo:pedropcamellon@83567517/folium@1174567174:environment:azure-demo`.
- `AZURE_DEMO_STATIC_WEB_APP_NAME` for the globally unique app name.
- `AZURE_DEMO_ACR_NAME` for the globally unique container registry name.
- `AZURE_DEMO_APPSERVICE_ENABLED=true` only after the App Service is provisioned
  and deployment is approved; also set `AZURE_DEMO_APPSERVICE_NAME` and
  `AZURE_DEMO_RESOURCE_GROUP`.

Grant that identity **Storage Blob Data Contributor** on the
`foliumdemotfstate/tfstate` container and **Contributor** only on
`rg-folium-demo`. Grant the same federated identity **AcrPush** on the demo
registry for CI image publishing; the Web App's system identity receives
**AcrPull** through Terraform. Because Terraform creates this role assignment,
its identity also needs role-assignment write permission scoped to
`rg-folium-demo` (for example, Role Based Access Control Administrator with a
role-assignment condition limiting grants to AcrPull), in addition to
Contributor. For the first run, create the resource group with an authorized
operator identity and import it into the demo state before using the GitHub
workflow; do not grant the workflow subscription-wide Contributor just to
create the group.

```bash
az group create --name rg-folium-demo --location "East US 2"
cd infrastructure/azure/demo
terraform init
terraform import \
  -var="subscription_id=$(az account show --query id --output tsv)" \
  -var="static_web_app_name=<globally-unique-name>" \
  -var="container_registry_name=<globally-unique-name>" \
  module.resource_group.azurerm_resource_group.this \
  "/subscriptions/$(az account show --query id --output tsv)/resourceGroups/rg-folium-demo"
```

In the `azure-demo` Environment settings, require reviewer approval for
deployments. Configure the Azure app registration's federated credential with
issuer `https://token.actions.githubusercontent.com` and audience
`api://AzureADTokenExchange`; no client secret is needed.
The repository is opted into GitHub's immutable OIDC subjects, so the owner
and repository numeric IDs in the subject are required.

Set the GitHub Actions deployment token without printing its value:

```bash
az staticwebapp secrets list --name <app-name> --resource-group rg-folium-demo \
  --query properties.apiKey --output tsv |
  gh secret set AZURE_STATIC_WEB_APPS_API_TOKEN
```

The Free tier has service limits; exceeding them may require a plan change.
No backend, database beyond the optional container registry, monitoring,
secrets vault, or model service is part of this target. Ensure the private
registry contains only the synthetic-data demo image.

## Teardown

Remove only the dedicated demo target:

```bash
cd infrastructure/azure/demo
terraform destroy \
  -var="subscription_id=$(az account show --query id --output tsv)" \
  -var="static_web_app_name=<globally-unique-name>" \
  -var="container_registry_name=<globally-unique-name>" \
  -var="enable_app_service_demo=true"
```

## Safety and limitations

The demo is for product demonstration and development only. It is not a
clinical system and must not be used with real patient information. Mock data
is synthetic and held in memory; changes do not persist. Mock mode does not
provide production authentication, persistence, or clinical decision support.

See the [local runtime guide](dev/local-development.md) for running the
complete application stack.
