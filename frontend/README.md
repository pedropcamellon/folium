# folium frontend

The Next.js frontend provides task-focused clinical workflow and review
surfaces. It calls the backend through centralized API configuration; UI
components do not hardcode API URLs or own workflow policy.

### Validate before merge

The **Check frontend demo** workflow builds the production Docker image and
smoke-tests its HTTP response on frontend branch pushes and pull requests.
It does not use Azure credentials or deploy. Failures appear as failed
GitHub checks and workflow error annotations; configure GitHub Actions
notification preferences for email/web alerts.

Build and run the same production image locally from the repository root:

```bash
docker build --build-arg NEXT_PUBLIC_API_MODE=mock -t folium-frontend-demo:check frontend
docker run --rm -p 3000:3000 folium-frontend-demo:check
```

Open `http://localhost:3000` to verify the container response. This tests the
same production image format intended for App Service, not Azure provisioning
or deployment.

## Local development

Start the supported local stack from the repository root:

```bash
uv run folium
```

See the [local runtime guide](../docs/dev/local-development.md) for
prerequisites and service controls. Use `pnpm build`, `pnpm lint`, and
`pnpm type-check` for frontend-only production build, lint, and TypeScript
checks.

See the [service boundaries](../docs/dev/architecture/service-boundaries.md)
for the frontend's role in the platform.

See [frontend boundaries](../docs/dev/frontend/overview.md) for the rationale
behind the current client architecture and workflow-state patterns.

## Azure mock demo deployment

The current demo remains on Azure Static Web Apps Free. Terraform can
optionally provision an Azure App Service Linux B1 plan and container Web App;
that paid environment is disabled by default and has not been provisioned.
The migration remains tracked in issue #88.

On pushes to `main`, the container check publishes the exact tested image to
GHCR under a commit-specific tag and deploys that digest only when the
`AZURE_DEMO_APPSERVICE_ENABLED` GitHub Environment variable is `true`. Before
enabling deployment, make the `folium-demo` GHCR package public so App Service
can pull it without registry credentials, and configure the `azure-demo`
Environment's Azure OIDC variables and approval protections. Successful
deployments update the URL in the deployment guide after an HTTP smoke test.

The prior Static Web Apps deployment relied on Oryx dependency resolution,
which did not consistently follow the repository's pnpm lockfile. It exposed
an ESLint peer dependency mismatch and then a Framer Motion / motion-dom
export mismatch. Building and smoke-testing the production container before
deployment validates the same locked dependency and runtime packaging
without requiring a paid Azure deployment.

The F1 plan's multi-app allowance does not include custom containers. The
minimum planned container tier is Linux B1, estimated at about $12.41/month
for 730 hours in East US 2 before taxes or incidental charges. The Terraform
switch is opt-in; do not apply it without reviewing current pricing.

See the [deployment guide](../docs/deployment.md) for credentials, production
URL, Terraform, and deployment verification.
