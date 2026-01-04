# Azure OpenAI Provider

Clinical summarization using Azure OpenAI Service with language models.

## Overview

Azure OpenAI provides access to advanced language models for generating structured clinical SOAP notes. The service uses Azure AI Inference SDK and supports HIPAA compliance with proper BAA setup.

## Prerequisites

- Azure OpenAI resource in your Azure subscription
- Model deployment created in Azure OpenAI Studio
- Business Associate Agreement (BAA) signed for HIPAA compliance
- API key or managed identity credentials

## Setup Steps

1. **Create Azure OpenAI Resource** in Azure Portal (select HIPAA-eligible region like East US)
2. **Deploy a model** in Azure OpenAI Studio (e.g., gpt-4o, gpt-4-turbo, gpt-35-turbo)
3. **Get credentials** (endpoint URL and API key from Azure Portal)
4. **Update service configuration** to use `azure` provider
5. **Select deployment** based on speed/cost/quality requirements

## HIPAA Compliance

Azure OpenAI supports HIPAA-compliant deployments:

- **Sign Azure BAA** via Azure Portal or support
- **Use eligible regions** (East US, West US 2, etc.)
- **Enable encryption** (TLS 1.2+ in transit, at rest by default)
- **Audit logging** via Azure Monitor
- **Data residency** stays in selected region
- **No training** on customer data

## Configuration

Set provider to `azure` and configure endpoint, API key, deployment name, and API version. See SPEC.md for detailed environment variables and docker-compose configuration.

## Common Issues

**Deployment not found**: Verify deployment name matches what you created in Azure OpenAI Studio

**Invalid credentials**: Check API key and endpoint URL (must include trailing slash)

**Rate limit exceeded**: Azure OpenAI has per-deployment rate limits; upgrade tier or implement retry logic

**Content filtering**: Azure applies content filters by default; request exemption for clinical content if needed

---
*See SPEC.md for detailed configuration, architecture, and code examples.*
