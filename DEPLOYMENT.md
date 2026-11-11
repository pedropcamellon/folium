# Frontend Demo

The frontend can run in mock mode for a hosted showcase without a backend, database, or external API. Mock mode returns synthetic data in the browser and does not send requests to the Folium backend.

## Build

Set `NEXT_PUBLIC_API_MODE=mock` in the frontend build environment. The setting is embedded at build time. Then build and run the Next.js app:

```bash
cd frontend
NEXT_PUBLIC_API_MODE=mock pnpm exec next build --no-lint
pnpm start
```

The no-lint flag is required while existing ESLint violations elsewhere in the frontend are being addressed. Next.js still performs TypeScript validation during this build.

In mock mode, the demo provider is signed in automatically. The patient and clinical records are synthetic, in-memory examples; changes made during a session are not persisted.

## Real Backend Mode

Omit `NEXT_PUBLIC_API_MODE` or set it to `real`, and set `NEXT_PUBLIC_API_URL` to the FastAPI backend URL. Real mode continues to use the configured backend services.

## Azure Static Web Apps

The frontend demo is deployed separately from the full-stack Azure environment.
Terraform in `infrastructure/azure/demo/` reuses only the resource-group and
Static Web Apps modules and selects the Free tier. Do not apply
`infrastructure/azure/`, which provisions backend and paid services.

Production demo URL (updated by GitHub Actions after each successful `main`
deployment):

<!-- demo-url:start -->
Pending first successful deployment.
<!-- demo-url:end -->

The GitHub Actions workflow deploys pushes to `main` and creates pull-request
preview deployments. Set the repository secret
`AZURE_STATIC_WEB_APPS_API_TOKEN` from the Static Web App deployment token.
Provision the isolated target with Azure CLI authentication:

```bash
cd infrastructure/azure/demo
terraform init
terraform apply \
  -var="subscription_id=$(az account show --query id --output tsv)" \
  -var="static_web_app_name=<globally-unique-name>"
```

Then set the deployment secret without printing its value:

```bash
az staticwebapp secrets list --name <app-name> --resource-group <resource-group> \
  --query properties.apiKey --output tsv |
  gh secret set AZURE_STATIC_WEB_APPS_API_TOKEN
```

Set `NEXT_PUBLIC_API_MODE=mock` at build time. The workflow records the
production URL returned by Azure after deployment; URL-only documentation
commits do not retrigger deployment.

Use the `demo` resource group and synthetic-data tags. The Free tier has
service limits; exceeding them may require a plan change. Delete only the
dedicated demo resource group to tear down the hosted demo:

```bash
cd infrastructure/azure/demo
terraform destroy \
  -var="subscription_id=$(az account show --query id --output tsv)" \
  -var="static_web_app_name=<globally-unique-name>"
```

## Scope and Safety

The mock showcase is for product demonstration and development only. It is
not a clinical system and must not be used with real patient information. Mock
data is synthetic, and mock mode does not provide production authentication,
persistence, or clinical decision support.
