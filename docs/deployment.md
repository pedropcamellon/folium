# Deployment Guide

## Synthetic static demo

The demo runs on Azure Static Web Apps **Free**, in Central US. It uses
browser-local synthetic fixtures, no Folium backend, and no server runtime.
It is not a clinical system or a production authentication boundary.
Demo edits are simulated in the browser, not persisted in a shared database.

Production demo URL (updated after each successful deployment and HTTP check):

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
Free with a portable static export.

The current approach builds once using the frozen pnpm lockfile and deploys
only the exported files with `skip_app_build` and `skip_api_build`. Oryx does
not reinstall dependencies, rebuild Next.js, or provision a hybrid SSR backend.
SWA's hybrid Next.js support is not used.

Only the demo resource group and Free SWA are managed by this Terraform root.
ACR, Container Apps, their identity and role assignment, and App Service hosting
are removed. Shared Terraform state storage is retained and may have its own
small storage/transaction charges; Free hosting does not mean every Azure
resource in the subscription is free.

## Build modes and routing

The normal application retains standalone output and dynamic patient routes.
Static export is enabled only with `NEXT_PUBLIC_DEMO_STATIC=true`, and requires
`NEXT_PUBLIC_API_MODE=mock`. Public assets use an optional
`NEXT_PUBLIC_BASE_PATH`; SWA uses the domain root, so it is empty.

```bash
cd frontend
NEXT_PUBLIC_DEMO_STATIC=true NEXT_PUBLIC_API_MODE=mock pnpm build --no-lint
pnpm type-check
```

In the static demo, patient links use `/patients/demo/?id=<id>` so records
created after build can render through one exported route. The standard
application continues using `/patients/<id>`. Static hosting does not run
Next.js middleware or image optimization; the demo uses unoptimized images
and browser-local mock behavior instead.

## Release pipeline

`demo-pipeline.yml` is the only demo entry point. PRs and branch pushes validate
Terraform and build/type-check the static export. The workflow also checks the
landing page, exported patient route, and static assets exist before uploading.

On main, validation is followed by Terraform plan/apply and deployment of the
same exported artifact using `Azure/static-web-apps-deploy`. OIDC authenticates
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
before teardown. Preserve shared state storage. Roll back by redeploying a
previously validated static artifact; rollback has not yet been live-tested.

## Verified evidence

On November 12, 2026 the exported app deployed successfully to the URL above.
Live browser checks loaded the provider dashboard, opened the seeded patient's
history, and created a synthetic patient whose query-based history route
rendered successfully. Dashboard/history navigation recorded no external or
backend requests and no page errors. The local export build, TypeScript check,
and nine-route/asset checks passed. CI deployment and preview acceptance work
remain tracked in issue #16; issue #88 preserves the Azure investigation.
