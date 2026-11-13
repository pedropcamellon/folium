# Deployment Guide

## Synthetic hybrid demo

The demo targets Azure Static Web Apps **Free**, in Central US, using its
preview hybrid Next.js hosting. It uses browser-local synthetic fixtures and
does not connect to the Folium backend.
It is not a clinical system or a production authentication boundary.
Demo edits are simulated in the browser, not persisted in a shared database.

Last successfully deployed demo URL (the current live revision is the previous
static export; this URL is not evidence that hybrid deployment succeeded):

<!-- demo-url:start -->
[https://salmon-island-0248c5310.3.azurestaticapps.net](https://salmon-island-0248c5310.3.azurestaticapps.net)
<!-- demo-url:end -->

### Hosting decisions and history

The original SWA deployment delegated dependency resolution and the Next.js
build to Oryx. Different dependency resolution exposed Motion build failures
and left the endpoint serving a placeholder. That was a build reliability
failure, not proof that SWA cannot host Next.js.

App Service F1 was explored next. It cannot host custom containers, so a ZIP
package was necessary. East US runtime suspension and inconsistent regional
quota enforcement also blocked that path. Central US creation was rejected
despite available quota reported by the quota API.

Container Apps successfully ran the tested container, but ACR Basic introduced
a standing registry charge. GHCR could remove that charge but still required
registry authorization and public package setup. The selected host is SWA
Free, now using hybrid Next.js hosting rather than static export.

Microsoft documents SWA hybrid Next.js support as preview. The SWA deployment
action builds the application from its source directory.

Only the demo resource group and Free SWA are managed by this Terraform root.
ACR, Container Apps, their identity and role assignment, and App Service hosting
are removed. Shared Terraform state storage is retained and may have its own
small storage/transaction charges; Free hosting does not mean every Azure
resource in the subscription is free.

## Build and routing

The frontend uses Next.js standalone output. Its build also packages `.next/static`
and `public` for the runtime. Mock mode is explicitly enabled for validation
and deployment.

```bash
cd frontend
NEXT_PUBLIC_API_MODE=mock pnpm build
pnpm type-check
```

Patient links use dynamic `/patients/<id>` routes. Middleware is pass-through
and excludes dotted paths, including SWA's documented `/.swa/health.html`
deployment probe. The demo's mock provider and fixtures remain browser-local;
no server action or clinical-data API route is added.

## Release pipeline

`demo-pipeline.yml` is the only demo entry point. PRs and branch pushes validate
Terraform and build/type-check the standalone Next.js app, checking its server
entrypoint and packaged static assets.

On main, validation is followed by Terraform plan/apply and deployment of the
hybrid Next.js app using `Azure/static-web-apps-deploy`. OIDC authenticates
the release to Azure; the SWA deployment token is retrieved at runtime and
masked. Required protected `azure-demo` Environment variables are
`AZURE_CLIENT_ID`, `AZURE_TENANT_ID`, and `AZURE_SUBSCRIPTION_ID`.
The release identity needs Contributor on the demo group and Storage Blob Data
Contributor on the state container. Provision the group with an authorized
operator if the release identity is resource-group-scoped.

The endpoint must return the actual synthetic demo marker, not merely HTTP 200,
before the workflow updates this guide's URL. Documentation-only commits do
not trigger deployment. Main runs queue rather than interrupting an apply.
Same-repository PRs deploy the validated artifact to SWA previews using the
repository secret `AZURE_STATIC_WEB_APPS_API_TOKEN`; previews skip explicitly
when the secret is unavailable. Fork PRs validate only and receive no deployment
credentials. Preview execution still requires verification after publication.

## Terraform, teardown, and rollback

Use `infrastructure/demo/`, not the full application root at
`infrastructure/azure/`. Both local and Actions runs use the same Blob backend
and historical `folium-demo-static-web-app.tfstate` key. Do not rename the key.

```bash
cd infrastructure/demo
terraform init -reconfigure
terraform plan -out=swa.tfplan -var="subscription_id=<subscription-id>"
terraform apply swa.tfplan
```

Neither `container_image` nor `enable_app_service_demo` exists in the SWA root.
Never apply an old ACA/F1 plan. After an interrupted apply, confirm no Terraform
writer is running before addressing a stale lock; do not bypass locking.

Disable the release workflow and review a destroy plan for this isolated root
before teardown. Preserve shared state storage. Roll back by redeploying a previously validated app revision; rollback has not
yet been live-tested.

## Validation and limitations

The prior static deployment was smoke-tested, but that is not evidence for the
hybrid runtime. Microsoft's published hybrid limitations include linked Azure
APIs and SWA CLI emulation/deployment; this demo uses neither. Azure deployment
and live smoke checks remain required before hybrid hosting is considered
verified. See issue #95 for pending Azure validation.
