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

The demo uses Free F1 App Service with its built-in Node runtime, not a custom
container. No paid B1 or ACR is provisioned. The former demo Static Web App
configuration and deployment workflow have been removed.

CI builds and HTTP-smoke-tests a glibc-based Docker image, exports its
standalone runtime as a ZIP, and tests the extracted package under clean Node.
F1 receives that package through Azure OIDC ZIP deployment. Docker is a build
and validation tool only; F1 cannot host custom containers. Protect the
`azure-demo` Environment with required approval. Successful deployments update
the documented URL after HTTP smoke testing.

The prior Static Web Apps deployment relied on Oryx dependency resolution,
which did not consistently follow the repository's pnpm lockfile. It exposed
an ESLint peer dependency mismatch and then a Framer Motion / motion-dom
export mismatch. Building and smoke-testing the production container before
deployment validates the same locked dependency and runtime packaging
without requiring a paid Azure deployment.

F1 has shared compute/storage limits and no production SLA. Provisioning is
opt-in; verify current quota and availability before applying Terraform.

See the [deployment guide](../docs/deployment.md) for credentials, production
URL, Terraform, and deployment verification.
