# CI/CD workflows

This directory contains the GitHub Actions workflows used to build, validate,
and promote folium.

## Current structure

- `deploy-backend.yml` is the manual promotion entry point. It selects the
  target environment and calls reusable build, approval, infrastructure, and
  provider deployment workflows.
- `build.yml` and `approval.yml` are reusable workflow building blocks.
- `azure-*.yml` and `aws-*.yml` contain provider-specific reusable deployment
  and Terraform workflows.
- `deploy-frontend.yml` manages frontend deployment separately.
- `docs.yml` publishes the documentation site.

Reusable workflows remain directly in `.github/workflows/` because GitHub
Actions does not resolve reusable workflows from subdirectories.

## Adding a cloud provider

1. Add a provider-prefixed reusable deployment workflow and, when needed, a
   Terraform workflow directly in this directory.
2. Give each reusable workflow typed `workflow_call` inputs for the deployment
   environment and its required configuration.
3. Add the provider as an explicit option in `deploy-backend.yml` and route it
   through the shared build and approval stages.
4. Verify the resulting promotion path against the target environment before
   presenting it as supported.

Cloud targets are planned deployment paths. See the [deployment order](../../docs/dev/architecture/deployment-order.md)
and [CI/CD promotion](../../docs/dev/operations/ci-cd-promotion.md) for the
reasoning behind this structure.
