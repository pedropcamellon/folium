# AWS Bedrock Infrastructure Setup

This directory contains Terraform configuration for AWS Bedrock access for the Folium clinical summarization service.

## Quick Start

### Prerequisites

1. **AWS Account** with Bedrock access
2. **Terraform** >= 1.0
3. **AWS CLI** configured (`aws configure`)
4. **Bedrock Model Access**: Request access to Claude models in AWS Console

### Setup

**1. Request Bedrock Model Access**

```bash
# In AWS Console:
# Bedrock → Model access → Request access to Claude 3 models
# Usually instant approval for Sonnet/Haiku
```

**2. Initialize Terraform**

```bash
cd infrastructure
terraform init
```

**3. Configure Variables**

```bash
# Create terraform.tfvars (gitignored)
cat > terraform.tfvars <<EOF
environment         = "dev"
aws_region          = "us-east-1"
create_dev_user     = true
log_retention_days  = 30
error_threshold     = 10
enable_audit_logs   = false
monthly_cost_budget = 100
EOF
```

**4. Plan and Apply**

```bash
# Preview changes
terraform plan

# Apply infrastructure
terraform apply
```

**5. Get Credentials**

```bash
# Output credentials for Docker Compose
terraform output -json docker_compose_config

# Or retrieve individual values
terraform output dev_access_key_id
terraform output -raw dev_secret_access_key
```

**6. Update docker-compose.yml**

```bash
# Export credentials
export AWS_ACCESS_KEY_ID=$(terraform output -raw dev_access_key_id)
export AWS_SECRET_ACCESS_KEY=$(terraform output -raw dev_secret_access_key)

# Or add to services/summarize/.env (gitignored)
cat > services/summarize/.env <<EOF
AWS_REGION=us-east-1
AWS_ACCESS_KEY_ID=${AWS_ACCESS_KEY_ID}
AWS_SECRET_ACCESS_KEY=${AWS_SECRET_ACCESS_KEY}
AWS_BEDROCK_MODEL=anthropic.claude-3-sonnet-20240229-v1:0
EOF
```

## Resources Created

| Resource | Purpose |
|----------|---------|
| **IAM Role** | Bedrock access for ECS/container environments |
| **IAM Policy** | Permissions for Claude model invocation |
| **IAM User** | Development credentials (optional) |
| **CloudWatch Logs** | API call logging and monitoring |
| **CloudWatch Alarms** | Error rate alerts |
| **SNS Topic** | Alert notifications |
| **Secrets Manager** | Secure credential storage |
| **S3 Bucket** | Audit logs (optional) |

## Security Best Practices

### HIPAA Compliance

1. **Sign AWS BAA**: Required before processing PHI
   - AWS Console → Support → Create Case → Account & Billing → "Request BAA"

2. **Enable Encryption**: Already configured in Terraform
   - All data encrypted in transit (TLS 1.2+)
   - Logs encrypted at rest (AES-256)

3. **Audit Logging**: Enable for production

   ```bash
   terraform apply -var="enable_audit_logs=true"
   ```

4. **Access Controls**:
   - Use IAM roles in production (not access keys)
   - Rotate dev access keys every 90 days
   - Enable MFA for all IAM users

### Access Key Rotation

```bash
# Rotate development access keys
terraform taint aws_iam_access_key.summarization_dev[0]
terraform apply

# Update environment variables with new keys
```

### Cost Monitoring

Monitor Bedrock usage:

```bash
# View metrics in CloudWatch
aws cloudwatch get-metric-statistics \
  --namespace "Folium/Summarization" \
  --metric-name "BedrockInvocations" \
  --start-time 2026-01-01T00:00:00Z \
  --end-time 2026-01-02T00:00:00Z \
  --period 3600 \
  --statistics Sum

# Estimate costs (assumes ~500 input + 200 output tokens per summary)
# Claude 3 Sonnet: $3/1M input tokens, $15/1M output tokens
# Per summary: ~$0.0015 = 1000 summaries costs ~$1.50
```

## Environments

| Environment | Region | Model | Budget/Month |
|-------------|--------|-------|--------------|
| **dev** | us-east-1 | Haiku | $25 |
| **staging** | us-east-1 | Sonnet | $50 |
| **production** | us-east-1 | Sonnet | $500 |

## Troubleshooting

### "Access denied to model"

- Verify model access granted in AWS Console
- Check IAM policy includes correct model ARN
- Wait 5-10 minutes after requesting access

### "Credentials not found"

- Verify `AWS_ACCESS_KEY_ID` and `AWS_SECRET_ACCESS_KEY` set
- Check credentials: `aws sts get-caller-identity`
- Ensure IAM user has Bedrock policy attached

### "Throttling exception"

- Check service quotas: AWS Console → Service Quotas → Bedrock
- Default limits: 1000 requests/minute (varies by model)
- Request quota increase if needed

### High costs

- Review CloudWatch metrics for invocation patterns
- Check `AWS_BEDROCK_MAX_TOKENS` setting (default 500)
- Consider switching to Haiku for high-volume workloads
- Enable cost alerts: `terraform apply -var="enable_cost_alerts=true"`

## Cleanup

```bash
# Destroy all resources
terraform destroy

# Destroy only AWS resources (keep Azure)
terraform destroy -target=aws_iam_role.summarization_service
```

## Architecture

```
┌─────────────────────────────────────────────────────────┐
│                  Folium Backend                     │
│                   (FastAPI 8000)                        │
└───────────────────┬─────────────────────────────────────┘
                    │
                    │ HTTP POST /summarize
                    ▼
┌─────────────────────────────────────────────────────────┐
│            Summarization Service                        │
│              (FastAPI 8002)                             │
└───────────────────┬─────────────────────────────────────┘
                    │
                    ├─ Local Provider → MediPhi-Clinical (CPU, 90s)
                    │
                    └─ Bedrock Provider ┐
                                         ▼
                    ┌────────────────────────────────────┐
                    │         AWS Bedrock                │
                    │  ┌──────────────────────────────┐ │
                    │  │  Claude 3 Sonnet (2-5s)      │ │
                    │  │  Claude 3 Haiku (1-3s)       │ │
                    │  └──────────────────────────────┘ │
                    │                                    │
                    │  IAM Role + Policy                 │
                    │  CloudWatch Logs                   │
                    │  SNS Alerts                        │
                    └────────────────────────────────────┘
```

## Next Steps

1. Request Bedrock model access
2. Apply Terraform configuration
3. Export AWS credentials
4. Update docker-compose.yml
5. Rebuild with PROVIDER=bedrock
6. Sign AWS BAA for HIPAA compliance
7. Configure CloudWatch dashboards
8. Set up SNS email subscriptions

---
**Status**: AWS Bedrock infrastructure ready for production

*2026-01-02 18:45:00*
