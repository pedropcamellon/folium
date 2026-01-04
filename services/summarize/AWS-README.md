# AWS Bedrock Provider

Clinical summarization using Anthropic Claude models via AWS Bedrock.

## Overview

AWS Bedrock provides access to Claude 3 models (Haiku, Sonnet, Opus) for generating structured clinical SOAP notes. The service uses the AWS SDK to invoke Bedrock models and supports HIPAA compliance with proper BAA setup.

## Prerequisites

- AWS account with Bedrock access
- IAM permissions: `bedrock:InvokeModel` for Claude models
- Business Associate Agreement (BAA) signed for HIPAA compliance
- AWS credentials configured (Access Key ID, Secret Access Key)

## Setup Steps

1. **Enable Bedrock Model Access** in AWS Console → Bedrock → Model access
2. **Request access** to Claude 3 models (Haiku, Sonnet, or Opus)
3. **Wait for approval** (usually instant for Haiku and Sonnet)
4. **Configure AWS credentials** via environment variables or AWS CLI
5. **Update service configuration** to use `bedrock` provider
6. **Select model** based on speed/cost/quality requirements

## Available Models

| Model | Speed | Cost per 1M Tokens | Quality | Use Case |
|-------|-------|-------------------|---------|----------|
| Claude 3 Haiku | 1-3s | $0.25 input / $1.25 output | Good | High-volume summaries |
| Claude 3 Sonnet | 2-5s | $3 input / $15 output | Excellent | Production workloads |
| Claude 3 Opus | 5-10s | $15 input / $75 output | Best | Complex clinical cases |

**Cost estimate**: ~$0.13 per 1,000 summaries (Haiku), ~$1.50 per 1,000 summaries (Sonnet)

## HIPAA Compliance

AWS Bedrock supports HIPAA-compliant deployments:

- **Sign AWS BAA** before processing PHI
- **Enable encryption** (in transit and at rest by default)
- **Audit logging** via CloudTrail
- **Data residency** in US regions only
- **No training** on customer data

## Configuration

Set provider to `bedrock` and configure AWS credentials, region, and model name. See SPEC.md for detailed environment variables and docker-compose configuration.

## Common Issues

**Access denied to model**: Request model access in AWS Console → Bedrock → Model access

**Credentials not found**: Verify AWS credentials are set via environment variables

**Throttling exception**: Bedrock has rate limits; implement exponential backoff or upgrade quota

---
*See SPEC.md for detailed configuration, architecture, and code examples.*
