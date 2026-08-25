# Folium Infrastructure

Multi-cloud infrastructure for the Folium healthcare EMR platform.

## Architecture

**Azure**: Main application (App Service, Storage, AI services)  
**AWS**: Optional AI services (Bedrock for Claude models)  
**Frontend**: Self-hosted Next.js

See `azure/SPEC.md` and `aws/SPEC.md` for detailed architecture diagrams.

## Directory Structure

```
infrastructure/
├── README.md                    # This file
├── terraform.tfvars.json        # Shared environment variables
│
├── azure/                       # Azure resources (main application)
│   ├── main.tf                  # App Service, Storage, Key Vault
│   ├── variables.tf             # Azure-specific variables
│   ├── outputs.tf               # Azure outputs
│   ├── backend.tf               # Azure state backend
│   └── README.md                # Azure deployment guide
│
└── aws/                         # AWS resources (AI services)
    ├── bedrock.tf               # Bedrock IAM, CloudWatch, SNS
    ├── variables.tf             # AWS-specific variables
    ├── outputs.tf               # AWS outputs (credentials)
    ├── backend.tf               # AWS state backend (S3)
    └── README.md                # AWS deployment guide
```

## Quick Start

**Prerequisites**: Terraform >= 1.0, Azure CLI, AWS CLI (optional)

**Deploy Azure** (required):

```powershell
cd azure
terraform init && terraform apply
```

**Deploy AWS** (optional - AI services only):

```powershell
cd aws
terraform init && terraform apply
```

See `azure/README.md` and `aws/README.md` for detailed setup instructions.

## Environments

| Environment | Azure Region | AWS Region | Purpose                |
| ----------- | ------------ | ---------- | ---------------------- |
| **dev**     | East US      | us-east-1  | Local development      |
| **staging** | East US      | us-east-1  | Pre-production testing |
| **prod**    | East US      | us-east-1  | Production             |

## Configuration

Edit `terraform.tfvars.json` for environment settings. See cloud-specific README files for detailed configuration options.

## State Management

**Azure**: Stored in Azure Storage Account `foliumtfstate`
**AWS**: Local state (dev) or S3 backend (production)

See cloud-specific README files for backend configuration.

## Cost Estimates

**Azure**: ~$5-15/month (App Service F1 free, Azure OpenAI consumption-based)  
**AWS**: ~$1-10/month (Bedrock consumption-based, optional)

See SPEC.md files for detailed breakdowns.

## Security

- HTTPS enforced (TLS 1.2+)
- Managed identities and IAM roles
- Encryption at rest and in transit
- HIPAA compliance: Requires BAA for both Azure and AWS

See cloud-specific SPEC.md files for detailed security configurations.

## Deployment Checklist

- [ ] Azure CLI authenticated (`az login`)
- [ ] Deploy Azure: `cd azure && terraform apply`
- [ ] (Optional) AWS CLI configured and deploy AWS
- [ ] Configure environment variables
- [ ] Test deployments

## Cleanup

```powershell
cd azure && terraform destroy
cd aws && terraform destroy
```

---

**Last Updated**: 2026-01-02  
**Maintained By**: Folium Team
