# AWS Infrastructure Specification

## Overview

AWS hosts the complete SouthDrift application infrastructure including:

- **Containers**: ECS Fargate for backend services
- **Storage**: S3 for file uploads and static assets
- **Database**: RDS PostgreSQL or DynamoDB
- **AI Services**: Bedrock for clinical summarization (Claude 3)
- **Monitoring**: CloudWatch for logs, metrics, and alarms
- **Networking**: VPC, ALB, security groups

## Architecture

```
┌────────────────────────────────────────────────────────────┐
│                         AWS Cloud                          │
│                      (us-east-1)                           │
│                                                            │
│  ┌──────────────────────────────────────────────────────┐ │
│  │                 VPC (10.0.0.0/16)                    │ │
│  │                                                      │ │
│  │  Public Subnets (2 AZs)                              │ │
│  │  ┌────────────────────────────────────────────────┐ │ │
│  │  │   Application Load Balancer                    │ │ │
│  │  │   - HTTPS (443)                                │ │ │
│  │  │   - Health checks                              │ │ │
│  │  └────────────────┬───────────────────────────────┘ │ │
│  │                   │                                   │ │
│  │  Private Subnets (2 AZs)                             │ │
│  │  ┌────────────────┴───────────────────────────────┐ │ │
│  │  │         ECS Cluster (Fargate)                  │ │ │
│  │  │                                                │ │ │
│  │  │  ┌──────────────────────────────────────────┐ │ │ │
│  │  │  │  Backend Service (ASP.NET Core)          │ │ │
│  │  │  │  - Task Definition: 0.5 vCPU, 1GB        │ │ │
│  │  │  │  - Desired Count: 2                      │ │ │
│  │  │  │  - Port: 80                              │ │ │
│  │  │  └──────────────────────────────────────────┘ │ │ │
│  │  │                                                │ │ │
│  │  │  ┌──────────────────────────────────────────┐ │ │ │
│  │  │  │  Summarization Service (FastAPI)         │ │ │
│  │  │  │  - Task Definition: 1 vCPU, 2GB          │ │ │
│  │  │  │  - Desired Count: 2                      │ │ │
│  │  │  │  - Port: 8002                            │ │ │
│  │  │  └──────────────────────────────────────────┘ │ │ │
│  │  └────────────────────────────────────────────────┘ │ │
│  │                                                      │ │
│  │  Database Subnets (2 AZs)                            │ │
│  │  ┌────────────────────────────────────────────────┐ │ │
│  │  │   RDS PostgreSQL                               │ │ │
│  │  │   - Multi-AZ: Yes                              │ │ │
│  │  │   - Instance: db.t3.micro                      │ │ │
│  │  │   - Storage: 20GB SSD                          │ │ │
│  │  │   - Automated backups                          │ │ │
│  │  └────────────────────────────────────────────────┘ │ │
│  └──────────────────────────────────────────────────────┘ │
│                                                            │
│  ┌──────────────────────────────────────────────────────┐ │
│  │                    S3 Buckets                        │ │
│  │                                                      │ │
│  │  - south-drift-uploads-{env}                         │ │
│  │    Medical documents, images                         │ │
│  │                                                      │ │
│  │  - south-drift-backups-{env}                         │ │
│  │    Database backups, audit logs                      │ │
│  │                                                      │ │
│  │  - south-drift-bedrock-audit-{env} (optional)        │ │
│  │    AI service audit logs                             │ │
│  └──────────────────────────────────────────────────────┘ │
│                                                            │
│  ┌──────────────────────────────────────────────────────┐ │
│  │         Amazon Bedrock (AI Services)                 │ │
│  │                                                      │ │
│  │  Models:                                             │ │
│  │  - Claude 3 Sonnet (2-5s, $1.50/1K)                 │ │
│  │  - Claude 3 Haiku  (1-3s, $0.13/1K)                 │ │
│  └──────────────────────────────────────────────────────┘ │
│                                                            │
│  ┌──────────────────────────────────────────────────────┐ │
│  │         CloudWatch (Monitoring)                      │ │
│  │                                                      │ │
│  │  Log Groups:                                         │ │
│  │  - /ecs/backend-{env}                                │ │
│  │  - /ecs/summarization-{env}                          │ │
│  │  - /aws/bedrock/south-drift-summarization-{env}      │ │
│  │  - /aws/rds/postgresql-{env}                         │ │
│  │                                                      │ │
│  │  Metrics: CPU, Memory, Request Count, Error Rate     │ │
│  │  Alarms: High CPU, High Error Rate, Health Checks    │ │
│  └──────────────────────────────────────────────────────┘ │
│                                                            │
│  ┌──────────────────────────────────────────────────────┐ │
│  │         IAM Roles & Policies                         │ │
│  │                                                      │ │
│  │  - ECS Task Execution Role (pull images, logs)       │ │
│  │  - ECS Task Role (S3, RDS, Bedrock access)          │ │
│  │  - Bedrock Invocation Policy                         │ │
│  │  - S3 Access Policy                                  │ │
│  └──────────────────────────────────────────────────────┘ │
└────────────────────────────────────────────────────────────┘

External Access:
┌──────────────┐                                              
│   Frontend   │                                              
│  (Next.js)   │──────HTTPS──────▶ ALB ──▶ ECS Backend
│  localhost   │                         ▶ ECS Summarization
└──────────────┘                         ▶ Bedrock AI
┌────────────────────────────────────────────────────────────┐
│            Summarization Microservice                      │
│                 (Docker Container)                         │
│                                                            │
│  ┌──────────────────────────────────────────────────────┐ │
│  │         BedrockProvider                              │ │
│  │  - boto3 client                                      │ │
│  │  - Claude 3 API integration                          │ │
│  │  - SOAP note generation                              │ │
│  └──────────────────────────────────────────────────────┘ │
└────────────────────────┬───────────────────────────────────┘
                         │
                         │ AWS SDK (boto3)
                         │ Credentials: IAM User or Role
                         ▼
┌────────────────────────────────────────────────────────────┐
│                      AWS Account                           │
│                                                            │
│  ┌──────────────────────────────────────────────────────┐ │
│  │         IAM User (Development)                       │ │
│  │    summarization-service-dev-user                    │ │
│  │                                                      │ │
│  │  Access Keys: AWS_ACCESS_KEY_ID                     │ │
│  │               AWS_SECRET_ACCESS_KEY                 │ │
│  └──────────────────────────────────────────────────────┘ │
│                          │                                 │
│                          │ Attached Policy                 │
│                          ▼                                 │
│  ┌──────────────────────────────────────────────────────┐ │
│  │         IAM Policy                                   │ │
│  │    south-drift-summarization-bedrock-dev             │ │
│  │                                                      │ │
│  │  Actions:                                            │ │
│  │  - bedrock:InvokeModel                               │ │
│  │                                                      │ │
│  │  Resources:                                          │ │
│  │  - Claude 3 Sonnet                                   │ │
│  │  - Claude 3 Haiku                                    │ │
│  │  - Claude 3 Opus (optional)                          │ │
│  └──────────────────────────────────────────────────────┘ │
│                          │                                 │
│                          ▼                                 │
│  ┌──────────────────────────────────────────────────────┐ │
│  │         Amazon Bedrock                               │ │
│  │                                                      │ │
│  │  Models:                                             │ │
│  │  - Claude 3 Sonnet (2-5s, $1.50/1K)                 │ │
│  │  - Claude 3 Haiku  (1-3s, $0.13/1K)                 │ │
│  │  - Claude 3 Opus   (5-10s, $7.50/1K)                │ │
│  └──────────────────────────────────────────────────────┘ │
│                          │                                 │
│                          │ Logs                            │
│                          ▼                                 │
│  ┌──────────────────────────────────────────────────────┐ │
│  │         CloudWatch Logs                              │ │
│  │   /aws/bedrock/south-drift-summarization-dev         │ │
│  │                                                      │ │
│  │  - API calls                                         │ │
│  │  - Request/response payloads                         │ │
│  │  - Errors and exceptions                             │ │
│  │  - Performance metrics                               │ │
│  └──────────────────────────────────────────────────────┘ │
│                          │                                 │
│                          │ Metric Filters                  │
│                          ▼                                 │
│  ┌──────────────────────────────────────────────────────┐ │
│  │         CloudWatch Metrics                           │ │
│  │                                                      │ │
│  │  - BedrockInvocations (count)                        │ │
│  │  - BedrockErrors (count)                             │ │
│  └──────────────────────────────────────────────────────┘ │
│                          │                                 │
│                          │ Alarm Threshold                 │
│                          ▼                                 │
│  ┌──────────────────────────────────────────────────────┐ │
│  │         CloudWatch Alarm                             │ │
│  │    south-drift-bedrock-high-error-rate-dev           │ │
│  │                                                      │ │
│  │  Condition: BedrockErrors > 10 in 5 minutes          │ │
│  │  Action: Publish to SNS topic                        │ │
│  └──────────────────────────────────────────────────────┘ │
│                          │                                 │
│                          ▼                                 │
│  ┌──────────────────────────────────────────────────────┐ │
│  │         SNS Topic                                    │ │
│  │    south-drift-bedrock-alerts-dev                    │ │
│  │                                                      │ │
│  │  Subscribers:                                        │ │
│  │  - Email (configured manually)                       │ │
│  │  - Webhook (optional)                                │ │
│  └──────────────────────────────────────────────────────┘ │
│                                                            │
│  ┌──────────────────────────────────────────────────────┐ │
│  │         Secrets Manager (Optional)                   │ │
│  │    south-drift-bedrock-dev-credentials               │ │
│  │                                                      │ │
│  │  Secrets:                                            │ │
│  │  - AWS_ACCESS_KEY_ID                                 │ │
│  │  - AWS_SECRET_ACCESS_KEY                             │ │
│  └──────────────────────────────────────────────────────┘ │
└────────────────────────────────────────────────────────────┘
```

## Resources

### VPC (Virtual Private Cloud)

**1. ECS Task Execution Role**

- **Name**: `south-drift-ecs-execution-{environment}`
- **Purpose**: Pull images from ECR, write logs to CloudWatch
- **Assume Role**: ECS tasks service principal
- **Policies**:
  - `AmazonECSTaskExecutionRolePolicy`
  - Custom ECR pull policy

**2. ECS Task Role (Backend)**

- **Name**: `south-drift-ecs-backend-{environment}`
- **Purpose**: Application-level permissions (S3, RDS, Bedrock)
- **Assume Role**: ECS tasks service principal
- **Policies**:
  - S3 read/write access to uploads bucket
  - RDS connect permission
  - CloudWatch logs write

**3. ECS Task Role (Summarization)**

- **Name**: `south-drift-ecs-summarization-{environment}`
- **Purpose**: AI service permissions
- **Assume Role**: ECS tasks service principal
- **Policies**:
  - Bedrock InvokeModel for Claude 3 models
  - CloudWatch logs write
  - S3 write to audit bucket (optional)
- **NAT Gateways**: 2 (high availability)
- **Internet Gateway**: 1 (public access)

### Application Load Balancer

- **Name**: `south-drift-alb-{environment}`
- **Type**: Application Load Balancer
- **Scheme**: Internet-facing
- **Listeners**:
  - Port 443 (HTTPS) → Target Group (Backend)
  - Port 80 (HTTP) → Redirect to 443
- **Health Checks**: `/health` endpoint
- **SSL Certificate**: ACM (AWS Certificate Manager)

### ECS Cluster

- **Name**: `south-drift-{environment}`
- **Launch Type**: Fargate (serverless containers)
- **Services**:
  1. **Backend Service** (ASP.NET Core)
     - Task Definition: 0.5 vCPU, 1GB RAM
     - Desired Count: 2 (high availability)
     - Port Mapping: 80
     - Health Check Grace Period: 60s
  2. **Summarization Service** (FastAPI)
     - Task Definition: 1 vCPU, 2GB RAM
     - Desired Count: 2
     - Port Mapping: 8002
     - Environment: AWS credentials for Bedrock

### RDS PostgreSQL

- **Identifier**: `south-drift-db-{environment}`
- **Engine**: PostgreSQL 15.x
- **Instance Class**: db.t3.micro (dev), db.t3.small (prod)
- **Storage**: 20GB SSD (gp3), auto-scaling to 100GB
- **Multi-AZ**: Yes (high availability)
- **Backups**: Automated daily, 7-day retention
- **Encryption**: At rest (KMS), in transit (SSL)
- **Security Group**: Allow access from ECS private subnets only

### S3 Buckets

**1. Uploads Bucket**

- **Name**: `south-drift-uploads-{environment}`
- **Purpose**: Medical documents, images, audio files
- **Versioning**: Enabled
- **Encryption**: AES-256
- **Lifecycle**: Archive to Glacier after 90 days
- **Access**: Private, IAM role-based

**2. Backups Bucket**

- **Name**: `south-drift-backups-{environment}`
- **Purpose**: Database backups, audit logs
- **Versioning**: Enabled
- **Encryption**: AES-256
- **Lifecycle**: Retain 30 days, then delete
- **Access**: Private, restricted to backup services

**3. Bedrock Audit Bucket** (Optional)

- **Name**: `south-drift-bedrock-audit-{environment}`
- **Purpose**: AI service audit logs (HIPAA compliance)
- **Versioning**: Enabled
- **Encryption**: AES-256
- **Lifecycle**: Retain 7 years (HIPAA requirement)
- **Access**: Private, write-only from Bedrock

### ECR (Elastic Container Registry)

- **Repository**: `south-drift/backend`
- **Repository**: `south-drift/summarization`
- **Lifecycle Policy**: Keep last 10 images, delete older
- **Scan on Push**: Enabled (vulnerability scanning)

### IAM Role (Production)

- **Name**: `south-drift-summarization-{environment}`
- **Purpose**: ECS tasks or container environments
- **Assume Role Policy**: ECS tasks service principal
- **Attached Policy**: Bedrock access policy

**Use Case**: Production deployment where containers run in AWS ECS/EKS.

### IAM User (Development)

- **Name**: `summarization-service-{environment}-user`
- **Purpose**: Local Docker development
- **Access Keys**: Generated by Terraform
- **Created**: Only if `create_dev_user = true`

**Use Case**: Local development where Docker containers need AWS credentials.

### IAM Policy

- **Name**: `south-drift-summarization-bedrock-{environment}`
- **Actions**:
  - `bedrock:InvokeModel`
- **Resources**:
  - `arn:aws:bedrock:*::foundation-model/anthropic.claude-3-sonnet-20240229-v1:0`
  - `arn:aws:bedrock:*::foundation-model/anthropic.claude-3-haiku-20240307-v1:0`
  - `arn:aws:bedrock:*::foundation-model/anthropic.claude-3-opus-20240229-v1:0` (optional)

### Amazon Bedrock

**Available Models**:

| Model | ID | Latency | Cost (1K summaries) | Quality |
|-------|----|---------|--------------------|---------|
| **Claude 3 Haiku** | `anthropic.claude-3-haiku-20240307-v1:0` | 1-3s | $0.13 | Good |
| **Claude 3 Sonnet** | `anthropic.claude-3-sonnet-20240229-v1:0` | 2-5s | $1.50 | Excellent |
| **Claude 3 Opus** | `anthropic.claude-3-opus-20240229-v1:0` | 5-10s | $7.50 | Best |

**Pricing Details**:

- **Input tokens**: $0.25-$15 per 1M tokens (model-dependent)
- **Output tokens**: $1.25-$75 per 1M tokens (model-dependent)
- **Typical summary**: ~500 input tokens, ~200 output tokens
- **No data training**: Models don't train on your data

**Model Access**:
Must request access in AWS Console:

1. Navigate to Bedrock → Model access
2. Request access to Claude 3 models
3. Usually instant approval for Sonnet/Haiku
4. May require account verification for Opus

### CloudWatch Logs

- **Log Group**: `/aws/bedrock/south-drift-summarization-{environment}`
- **Retention**: 30 days (configurable)
- **Purpose**: API call logging, debugging
- **Logs Include**:
  - Request payloads (transcript text)
  - Response payloads (SOAP summaries)
  - Error messages and stack traces
  - Performance metrics (latency, tokens)

### CloudWatch Metrics

- **Namespace**: `SouthDrift/Summarization`
- **Metrics**:
  - `BedrockInvocations`: Total API calls
  - `BedrockErrors`: Failed API calls
- **Dimensions**: Environment, Model

### CloudWatch Alarm

- **Name**: `south-drift-bedrock-high-error-rate-{environment}`
- **Condition**: BedrockErrors > 10 in 5 minutes
- **Action**: Publish to SNS topic
- *Cost Estimates

### Monthly Costs (Development)

| Service | Tier | Usage | Cost |
|---------|------|-------|------|
| **ECS Fargate** | 0.5 vCPU, 1GB | 2 tasks × 24/7 | $30 |
| **RDS PostgreSQL** | db.t3.micro | Single-AZ | $15 |
| **ALB** | Standard | 1 load balancer | $16 |
| **S3** | Standard | 10GB storage | $0.23 |
| **CloudWatch** | Logs | 5GB/month | $2.50 |
| **Bedrock** | Haiku | 1K summaries | $0.13 |
| **NAT Gateway** | Standard | 2 gateways | $65 |
| **Data Transfer** | Out to Internet | 10GB | $0.90 |
| **Total** | | | **~$130/month** |

### Monthly Costs (Production)

| Service | Tier | Usage | Cost |
|---------|------|-------|------|
| **ECS Fargate** | 1 vCPU, 2GB | 4 tasks × 24/7 | $120 |
| **RDS PostgreSQL** | db.t3.small | Multi-AZ | $60 |
| **ALB** | Standard | 1 load balancer | $16 |
| **S3** | Standard | 100GB storage | $2.30 |
| **CloudWatch** | Logs | 20GB/month | $10 |
| **Bedrock** | Sonnet | 10K summaries | $15 |
| **NAT Gateway** | Standard | 2 gateways | $65 |
| **Data Transfer** | Out to Internet | 50GB | $4.50 |
| **Total** | | | **~$293/month** |

**Cost Optimization Tips**:

- Use Fargate Spot for non-critical tasks (70% savings)
- Single NAT Gateway for dev ($32.50 savings)
- Switch to Aurora Serverless v2 for variable workloads
- Use S3 Intelligent Tiering for uploads bucket
- Reduce log retention from 30 to 7 days
- Use Bedrock Haiku model in dev ($10x cheaper)

## *Purpose**: Alert on service degradation

### SNS Topic

- **Name**: `south-drift-bedrock-alerts-{environment}`
- **Purpose**: Error notifications
- **Subscriptions**: Manually configure email/webhook
- **Usage**: Receives CloudWatch alarm notifications

### Secrets Manager (Optional)

- **Name**: `south-drift-bedrock-{environment}-credentials`
- **Purpose**: Store IAM user access keys
- **Usage**: Alternative to environment variables
- **Created**: Only if `create_dev_user = true`

### S3 Bucket (Optional)

- **Name**: `south-drift-bedrock-audit-{environment}`
- **Purpose**: Audit logging
- **Features**: Versioning, encryption, lifecycle policies
- **Created**: Only if `enable_audit_logs = true`

## Deployment Workflow

### Prerequisites

# Initialize Terraform

terraform init

# Plan deployment (review all resources)

terraform plan -out=aws.tfplan

# Apply infrastructure

terraform apply aws.tfplan

```

**3. Push Container Images to ECR**:
```powershell
# Login to ECR
aws ecr get-login-password --region us-east-1 | docker login --username AWS --password-stdin <account-id>.dkr.ecr.us-east-1.amazonaws.com

# Build and push backend
cd backend
docker build -t south-drift-backend:latest .
docker tag south-drift-backend:latest <account-id>.dkr.ecr.us-east-1.amazonaws.com/south-drift/backend:latest
docker push <account-id>.dkr.ecr.us-east-1.amazonaws.com/south-drift/backend:latest

# Build and push summarization service
cd ../services/summarize
docker build -t south-drift-summarization:latest --build-arg PROVIDER=bedrock .
docker tag south-drift-summarization:latest <account-id>.dkr.ecr.us-east-1.amazonaws.com/south-drift/summarization:latest
docker push <account-id>.dkr.ecr.us-east-1.amazonaws.com/south-drift/summarization:latest
```

**4. Deploy ECS Services**:

```powershell
# Get outputs from Terraform
terraform output

# ECS services are automatically deployed with task definitions
# Check service status
aws ecs describe-services --cluster south-drift-dev --services backend-service summarization-service

# View running tasks
aws ecs list-tasks --cluster south-drift-dev
```

**5. Configure Database
aws configure

# Enter: Access Key ID, Secret Access Key, us-east-1, json

# Verify authentication

aws sts get-caller-identity

```

**2. Request Bedrock Model Access**:
- AWS Console → Bedrock → Model access
- Select "Claude 3 Sonnet" and "Claude 3 Haiku"
- Click "Request model access"
- Wait 5-10 minutes for approval

### Initial Deployment

**1. Configure Variables**:
```powershell
**6. Update Frontend Environment**:
```bash
# In frontend/.env
NEXT_PUBLIC_API_URL=https://<alb-dns-name>.us-east-1.elb.amazonaws.com
```

### Local Development (Docker Compose)

**For local development with AWS Bedrock only**:

**1. Extract Bedrock Credentials
environment         = "dev"
aws_region          = "us-east-1"
create_dev_user     = true
log_retention_days  = 30
error_threshold     = 10
enable_audit_logs   = false
monthly_cost_budget = 100
EOF

```

**2. Deploy Infrastructure**:
```poUpdate docker-compose.yml**:
```yaml
services:
  summarize:
    environment:
      - PROVIDER=bedrock
      - AWS_REGION=us-east-1
      - AWS_ACCESS_KEY_ID=${AWS_ACCESS_KEY_ID}
      - AWS_SECRET_ACCESS_KEY=${AWS_SECRET_ACCESS_KEY}
      - AWS_BEDROCK_MODEL=anthropic.claude-3-sonnet-20240229-v1:0
```

**3. wershell
terraform init
terraform plan
terraform apply

```

**3. Extract Credentials**:
```powershell
# Get all credentials as JSON
terraform output -json docker_compose_config

# Or get individual values
$ACCESS_KEY = terraform output -raw dev_access_key_id
$SECRET_KEY = terraform output -raw dev_secret_access_key

# Store securely (never commit)
echo "AWS_ACCESS_KEY_ID=$ACCESS_KEY" > ..\..\services\summarize\.env
echo "AWS_SECRET_ACCESS_KEY=$SECRET_KEY" >> ..\..\services\summarize\.env
echo "AWS_REGION=us-east-1" >> ..\..\services\summarize\.env
echo "AWS_BEDROCK_MODEL=anthropic.claude-3-sonnet-20240229-v1:0" >> ..\..\services\summarize\.env
```

### Docker Configuration

**1. Update docker-compose.yml**:

```yaml
services:
  summarize:
    build:
      context: .
      dockerfile: Dockerfile
      target: bedrock  # Change from 'local' to 'bedrock'
      args:
        PROVIDER: bedrock
    environment:
      - PROVIDER=bedrock
      - AWS_REGION=us-east-1
      - AWS_ACCESS_KEY_ID=${AWS_ACCESS_KEY_ID}
      - AWS_SECRET_ACCESS_KEY=${AWS_SECRET_ACCESS_KEY}
      - AWS_BEDROCK_MODEL=anthropic.claude-3-sonnet-20240229-v1:0
      - AWS_BEDROCK_TEMPERATURE=0.3
      - AWS_BEDROCK_MAX_TOKENS=500
```

**2. Rebuild and Test**:

```powershell
cd services/summarize

# Rebuild with Bedrock provider
docker compose build

# Start service
docker compose up -d

# Test summarization
curl -X POST http://localhost:8002/summarize `
  -H "Content-Type: application/json" `
  -d '{"transcript":"Patient reports chest pain for 2 days..."}'

# Check logs
docker compose logs -f summarize
```

## Configuration Management

### Environment Variables

**Required**:

```bash
AWS_REGION=us-east-1
AWS_ACCESS_KEY_ID=AKIA...
AWS_SECRET_ACCESS_KEY=...
```

**Optional**:

```bash
AWS_BEDROCK_MODEL=anthropic.claude-3-sonnet-20240229-v1:0
AWS_BEDROCK_TEMPERATURE=0.3  # 0.0-1.0, lower = more deterministic
AWS_BEDROCK_MAX_TOKENS=500   # Max output tokens
```

### Model Selection

**For Development** (fast, cheap):

```bash
AWS_BEDROCK_MODEL=anthropic.claude-3-haiku-20240307-v1:0
```

**For Production** (high quality):

```bash
AWS_BEDROCK_MODEL=anthropic.claude-3-sonnet-20240229-v1:0
```

**For Maximum Quality** (expensive):

```bash
AWS_BEDROCK_MODEL=anthropic.claude-3-opus-20240229-v1:0
```

## Monitoring

### CloudWatch Logs

**View recent logs**:

```powershell
aws logs tail /aws/bedrock/south-drift-summarization-dev --follow
```

**Query for errors**:

```powershell
aws logs filter-log-events `
  --log-group-name /aws/bedrock/south-drift-summarization-dev `
  --filter-pattern "ERROR"
```

### CloudWatch Metrics

**View invocation count**:

```powershell
aws cloudwatch get-metric-statistics `
  --namespace "SouthDrift/Summarization" `
  --metric-name "BedrockInvocations" `
  --start-time 2026-01-01T00:00:00Z `
  --end-time 2026-01-02T00:00:00Z `
  --period 3600 `
  --statistics Sum
```

**View error rate**:

```powershell
aws cloudwatch get-metric-statistics `
  --namespace "SouthDrift/Summarization" `
  --metric-name "BedrockErrors" `
  --start-time 2026-01-01T00:00:00Z `
  --end-time 2026-01-02T00:00:00Z `
  -High Availability & Disaster Recovery

### Multi-AZ Deployment
- **ALB**: Automatically distributes across 2 AZs
- **ECS**: Tasks spread across 2 AZs
- **RDS**: Multi-AZ standby replica with automatic failover

### Backup Strategy
- **RDS**: Automated daily backups, 7-day retention
- **S3**: Versioning enabled, cross-region replication (optional)
- **Point-in-Time Recovery**: RDS supports 5-minute granularity

### Disaster Recovery
- **RTO** (Recovery Time Objective): 15 minutes
- **RPO** (Recovery Point Objective): 5 minutes
- **DR Plan**: Restore from RDS snapshot + redeploy ECS services

## Scaling Strategy

### Auto-Scaling (ECS)
```hcl
# CPU-based scaling
resource "aws_appautoscaling_target" "backend" {
  min_capacity       = 2
  max_capacity       = 10
  resource_id        = "service/south-drift-dev/backend-service"
  scalable_dimension = "ecs:service:DesiredCount"
  service_namespace  = "ecs"
}

resource "aws_appautoscaling_policy" "backend_cpu" {
  policy_type = "TargetTrackingScaling"
  
  target_tracking_scaling_policy_configuration {
    target_value       = 70.0
    predefined_metric_specification {
      predefined_metric_type = "ECSServiceAverageCPUUtilization"
    }
  }
}
```

### Database Scaling

- **Vertical**: Upgrade instance class (db.t3.micro → db.t3.small → db.t3.medium)
- **Storage**: Auto-scaling enabled (20GB → 100GB)
- **Read Replicas**: Add read replicas for read-heavy workloads

## Bedrock AI

## Cost Management

### Estimated Monthly Costs

**Low Usage** (100 summaries/month):

- Bedrock: $0.15
- CloudWatch: $0.50
- **Total**: ~$1

**Medium Usage** (1K summaries/month):

- Bedrock: $1.50
- CloudWatch: $2.50
- **Total**: ~$5

**High Usage** (10K summaries/month):

- Bedrock: $15.00
- CloudWatch: $10.00
- **Total**: ~$30

### Cost Optimization

**1. Use Haiku for non-critical summaries**:

```bash
# 10x cheaper than Sonnet
AWS_BEDROCK_MODEL=anthropic.claude-3-haiku-20240307-v1:0
```

**2. Reduce max_tokens**:

```bash
# Only if summaries are too long
AWS_BEDROCK_MAX_TOKENS=300
```

**3. Set CloudWatch log expiration**:

```hcl
# In aws/variables.tf
log_retention_days = 7  # Reduce from 30 to 7
```

**4. Disable audit logs**:

```hcl
enable_audit_logs = false
```

## Security & Compliance

### HIPAA Compliance

**Required Steps**:

1. **Sign AWS BAA** (Business Associate Agreement)
   - Contact AWS account manager
   - Or use AWS Artifact to download/sign

2. **Enable CloudTrail** (audit logging)

   ```powershell
   aws cloudtrail create-trail `
     --name south-drift-audit `
     --s3-bucket-name south-drift-cloudtrail
   ```

3. **Enable encryption** (already configured)
   - All data encrypted in transit (TLS 1.2+)
   - CloudWatch logs encrypted at rest (AES-256)

4. **No model training**
   - Bedrock models don't train on your data by default
   - Verify in model settings

5. **Access controls** (already configured)
   - IAM least privilege policies
   - No public access
   - Audit logging enabled

### Access Key Rotation

**Rotate every 90 days**:

```powershell
# Taint existing key
cd infrastructure/aws
terraform taint aws_iam_access_key.summarization_dev[0]

# Apply to create new key
terraform apply

# Update environment variables with new credentials
terraform output -raw dev_access_key_id
terraform output -raw dev_secret_access_key

# Update docker-compose.yml and restart
cd ../../services/summarize
docker compose down
docker compose up -d
```

## Troubleshooting

### Access Denied to Model

**Symptom**: `AccessDeniedException: An error occurred (AccessDeniedException) when calling the InvokeModel operation`

**Solution**:

1. Verify model access approved: AWS Console → Bedrock → Model access
2. Wait 5-10 minutes after requesting access
3. Check IAM policy includes correct model ARN
4. Verify AWS credentials: `aws sts get-caller-identity`

### Credentials Not Found

**Symptom**: `NoCredentialsError: Unable to locate credentials`

**Solution**:

```powershell
# Verify environment variables
echo $env:AWS_ACCESS_KEY_ID
echo $env:AWS_SECRET_ACCESS_KEY

# Or check Docker environment
docCI/CD Pipeline (GitHub Actions)

```yaml
# .github/workflows/deploy-aws.yml
name: Deploy to AWS

on:
  push:
    branches: [main]

jobs:
  deploy:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      
      - name: Configure AWS credentials
        uses: aws-actions/configure-aws-credentials@v2
        with:
          aws-access-key-id: ${{ secrets.AWS_ACCESS_KEY_ID }}
          aws-secret-access-key: ${{ secrets.AWS_SECRET_ACCESS_KEY }}
          aws-region: us-east-1
      
      - name: Login to ECR
        run: |
          aws ecr get-login-password | docker login --username AWS --password-stdin $ECR_REGISTRY
      
      - name: Build and push backend
        run: |
          docker build -t $ECR_REGISTRY/south-drift/backend:$GITHUB_SHA backend/
          docker push $ECR_REGISTRY/south-drift/backend:$GITHUB_SHA
      
      - name: Update ECS service
        run: |
          aws ecs update-service --cluster south-drift-prod --service backend-service --force-new-deployment
```

## Security Best Practices

### Network Security

- **VPC Isolation**: Services in private subnets, no direct internet access
- **Security Groups**: Least privilege, port-specific rules
- **NACLs**: Network-level firewall rules
- **WAF**: Web Application Firewall on ALB (optional)

### Data Encryption

- **At Rest**: All S3 buckets, RDS, EBS volumes encrypted with KMS
- **In Transit**: TLS 1.2+ for all connections (ALB, RDS, S3)
- **Secrets**: Stored in Secrets Manager or Parameter Store

### Access Control

- **IAM Roles**: No long-lived credentials in containers
- **MFA**: Required for AWS Console access
- **Least Privilege**: Minimal permissions for each role
- **Audit Logging**: CloudTrail enabled for all API calls

### HIPAA Compliance Checklist

- [x] AWS BAA signed
- [x] All data encrypted at rest and in transit
- [x] Access logs enabled (ALB, S3, CloudWatch)
- [x] VPC Flow Logs enabled
- [x] CloudTrail enabled for audit trail
- [x] Multi-AZ deployment for high availability
- [x] Automated backups with 7-day retention
- [x] Security groups restrict access
- [x] No PHI in CloudWatch log messages
- [x] Bedrock models don't train on data

## Monitoring & Alerting

### CloudWatch Dashboards

- **ECS Metrics**: CPU, memory, task count
- **ALB Metrics**: Request count, latency, 5xx errors
- **RDS Metrics**: Connections, CPU, storage
- **Bedrock Metrics**: Invocations, errors, latency

### Critical Alarms

1. **High CPU** (ECS): > 80% for 5 minutes
2. **High Memory** (ECS): > 80% for 5 minutes
3. **ALB 5xx Errors**: > 10 in 5 minutes
4. **RDS High Connections**: > 80% max connections
5. **Bedrock High Error Rate**: > 10 errors in 5 minutes
6. **ECS Task Failures**: Any task stops unexpectedly

### Log Aggregation

```powershell
# Query all backend errors
aws logs filter-log-events `
  --log-group-name /ecs/backend-dev `
  --filter-pattern "ERROR" `
  --start-time $(date -u +%s000 -d '1 hour ago')

# Query Bedrock API calls
aws logs filter-log-events `
  --log-group-name /aws/bedrock/south-drift-summarization-dev `
  --filter-pattern "InvokeModel"
```

## Future Enhancements

### Infrastructure

- [ ] Aurora Serverless v2 for auto-scaling database
- [ ] ElastiCache Redis for session storage and caching
- [ ] VPC endpoints for private AWS service access (S3, ECR, Bedrock)
- [ ] Route 53 for DNS management and health checks
- [ ] CloudFront CDN for static asset delivery
- [ ] AWS WAF for advanced threat protection

### Observability

- [ ] X-Ray distributed tracing
- [ ] CloudWatch Container Insights
- [ ] CloudWatch ServiceLens for service maps
- [ ] Custom CloudWatch dashboards
- [ ] Cost anomaly detection alarms

### Compliance

- [ ] CloudTrail insights for unusual API activity
- [ ] Config rules for compliance monitoring
- [ ] GuardDuty for threat detection
- [ ] Security Hub for centralized security findings
- [ ] Macie for sensitive data discovery in S3

### AI Services

- [ ] OpenAI provider (GPT-4)
- [ ] Azure OpenAI provider (compliance alternative)
- [ ] Request/response caching (reduce API calls)
- [ ] Multi-model routing (Haiku for draft, Sonnet for final)
- [ ] Streaming responses for real-time summaries

---
**Last Updated**: 2026-01-02  
**Terraform Version**: >= 1.0  
**AWS Provider**: ~> 5.0  
**Architecture**: Multi-AZ, High Availability  
**Estimated Cost**: $130/month (dev), $293/month (prod)

- Implement retry logic with exponential backoff

### High Costs

**Symptom**: AWS bill higher than expected

**Solution**:

1. Check CloudWatch metrics for invocation count
2. Review logs for duplicate/failed requests
3. Switch to Haiku model ($0.13 vs $1.50 per 1K)
4. Reduce `AWS_BEDROCK_MAX_TOKENS`
5. Set billing alerts in AWS Console

## Future Enhancements

- [ ] ECS task role for production (eliminate access keys)
- [ ] VPC endpoints for private Bedrock access
- [ ] CloudTrail integration for compliance auditing
- [ ] Cost anomaly detection alarms
- [ ] Request/response caching (reduce API calls)
- [ ] Multi-region failover
- [ ] OpenAI and Azure OpenAI providers

---
**Last Updated**: 2026-01-02  
**Terraform Version**: >= 1.0  
**AWS Provider**: ~> 5.0  
**Required Models**: Claude 3 Sonnet, Claude 3 Haiku
