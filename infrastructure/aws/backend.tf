# AWS Terraform State Backend
# For production, use S3 backend. For local dev, comment this out.

# terraform {
#   backend "s3" {
#     bucket         = "south-drift-terraform-state"
#     key            = "aws/bedrock/terraform.tfstate"
#     region         = "us-east-1"
#     encrypt        = true
#     dynamodb_table = "terraform-state-lock"
#   }
# }

# Local backend (default) - state stored in .terraform/
# No configuration needed, Terraform uses local backend by default
