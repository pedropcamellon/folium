# Deployment Guide

## Azure mock frontend demo

The demo showcases synthetic data without a backend or database. Hosting uses
Free Linux F1 App Service with its built-in Node runtime. F1 cannot run custom
containers: Docker is used to build and validate the standalone package, not
as the Azure hosting runtime. No B1 plan or Azure Container Registry is created.
F1 has shared CPU/storage quotas and no production SLA; validate subscription
availability and limits before provisioning.

Production demo URL (updated after each successful deployment and HTTP check):

<!-- demo-url:start -->
Pending first successful deployment.
<!-- demo-url:end -->

## Build and release

The frontend workflow builds a glibc-based Linux Docker image from the frozen
pnpm lockfile, smoke-tests it, and exports its standalone runtime as a ZIP.
PR checks also unpack and test that ZIP under a clean Node runtime and load
the native Sharp dependency. ZIP creation preserves pnpm dependency symlinks.
Main releases deploy the same tested package,
without Oryx rebuilding dependencies. Docker build and Azure runtime use Node 20.

`demo-pipeline.yml` is the only entry point. PRs and branch pushes validate
Terraform and build/test the frontend package without Azure credentials.
Pushes to `main` (including merges) and manual dispatch on `main` run:

1. `demo-validate.yml`: validate Terraform and build/test the release ZIP.
2. `demo-infra.yml`: plan and apply the Free F1 environment using OIDC.
3. `demo-deploy.yml`: deploy the same run's tested ZIP and update the URL.

Each stage requires the previous stage to succeed. The children use
`workflow_call` only and have no independent push/PR triggers. Protect the
`azure-demo` Environment with required approval and configure its variables:

- `AZURE_CLIENT_ID`, `AZURE_TENANT_ID`, `AZURE_SUBSCRIPTION_ID`.
- `AZURE_DEMO_RESOURCE_GROUP`.

Use an Entra federated credential for the repository's `azure-demo` Environment
with issuer `https://token.actions.githubusercontent.com` and audience
`api://AzureADTokenExchange`. Use the repository's configured immutable OIDC
subject. No client secret or registry credentials are required.

Terraform is reconciled on every main release before deployment; no manual
enable flag is required. The deployed endpoint must pass HTTP
checks before the workflow updates this guide. URL-only commits do not match
deployment path filters. Deployments are serialized; no Azure deployment runs
on PRs.

## Terraform

Use `infrastructure/demo/` for the standalone mock demo. Use
`infrastructure/azure/` for the full Folium Azure application. These roots
serve different purposes and must not be interchanged. F1
provisioning is opt-in. The dedicated backend retains the historical
`folium-demo-static-web-app.tfstate` key for state continuity. Do not rename
the key or discard state during this migration.

Local plan/apply and GitHub Actions use this same Azure Blob remote state.
After moving the Terraform root, initialize locally with `-reconfigure` so a
previous validation-only local backend is not reused. The `-backend=false`
option is only for CI validation and must not be used for plan or apply.

```bash
cd infrastructure/demo
az login
az account set --subscription "<subscription-id>"
terraform init -reconfigure
terraform plan -out=tfplan \
  -var="subscription_id=$(az account show --query id --output tsv)" \
  -var="enable_app_service_demo=true"
```

default resource group: `rg-folium-demo`, East US. App Service defaults to
`folium-demo` (renamed from `folium-demo-free`); override the globally unique
Web App name if necessary. Review the plan before applying: it removes the
former demo Static Web App from state and adds F1 hosting. The operator has
already removed the live Static Web App; refresh and review the plan to
reconcile that deletion. Disabling the optional flag after
provisioning plans destruction of the App Service resources.

The pipeline applies Terraform only on main in the protected Environment,
explicitly enabling the Free F1 resources. Configure required Environment
reviewers before merging. New non-main runs cancel older runs for the same
source branch, including duplicate push/PR runs. Main runs queue rather than
interrupting an in-progress apply or release.
Grant the identity Contributor scoped to the demo resource group and Storage
Blob Data Contributor on the state container. Your local Azure CLI identity
also needs Storage Blob Data Contributor on that same container. Bootstrap/import the resource
group with an authorized operator rather than granting subscription-wide access.

## Rollback and teardown

Retain a known-good release ZIP outside the short-lived CI artifact retention
window. Roll back by redeploying that package through the protected workflow
process and repeating HTTP/mock-flow checks. Reverting code alone does not
restore the removed Static Web App. Rollback has not yet been live-tested.

Disable the parent pipeline before teardown. Review a destroy plan
using the same subscription and `enable_app_service_demo=true` inputs; destroy
only the isolated demo target, never the full-stack root.

## Safety

Use synthetic data only. This demo is not a clinical system and does not provide
production authentication or persistence. Live deployment, quota validation,
browser network checks, URL-commit behavior, and rollback remain acceptance
checks rather than verified outcomes.
