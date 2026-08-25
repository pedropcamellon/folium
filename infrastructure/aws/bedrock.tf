# AWS Infrastructure for Folium Summarization Service
# Provisions IAM roles, policies, and Bedrock access

terraform {
  required_version = ">= 1.0"
  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 5.0"
    }
  }
}

provider "aws" {
  region = var.aws_region

  default_tags {
    tags = {
      Environment = var.environment
      Project     = "south-drift"
      ManagedBy   = "terraform"
      Service     = "summarization"
    }
  }
}

# IAM Role for Summarization Service
resource "aws_iam_role" "summarization_service" {
  name = "south-drift-summarization-${var.environment}"

  assume_role_policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Action = "sts:AssumeRole"
        Effect = "Allow"
        Principal = {
          Service = "ecs-tasks.amazonaws.com"
        }
      }
    ]
  })

  tags = {
    Name = "south-drift-summarization-role"
  }
}

# IAM Policy for Bedrock Access
resource "aws_iam_policy" "bedrock_access" {
  name        = "south-drift-bedrock-access-${var.environment}"
  description = "Allow summarization service to invoke Bedrock models"

  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Effect = "Allow"
        Action = [
          "bedrock:InvokeModel",
          "bedrock:InvokeModelWithResponseStream"
        ]
        Resource = [
          "arn:aws:bedrock:${var.aws_region}::foundation-model/anthropic.claude-3-haiku-20240307-v1:0"
        ]
      }
    ]
  })
}

# Attach Bedrock policy to role
resource "aws_iam_role_policy_attachment" "summarization_bedrock" {
  role       = aws_iam_role.summarization_service.name
  policy_arn = aws_iam_policy.bedrock_access.arn
}

# IAM User for local development / Docker containers
resource "aws_iam_user" "summarization_dev" {
  count = var.create_dev_user ? 1 : 0
  name  = "south-drift-summarization-dev-${var.environment}"

  tags = {
    Name        = "summarization-dev-user"
    Environment = var.environment
  }
}

# Access key for dev user (use with caution, rotate regularly)
resource "aws_iam_access_key" "summarization_dev" {
  count = var.create_dev_user ? 1 : 0
  user  = aws_iam_user.summarization_dev[0].name
}

# Attach Bedrock policy to dev user
resource "aws_iam_user_policy_attachment" "summarization_dev_bedrock" {
  count      = var.create_dev_user ? 1 : 0
  user       = aws_iam_user.summarization_dev[0].name
  policy_arn = aws_iam_policy.bedrock_access.arn
}

# CloudWatch Log Group for Bedrock API calls
resource "aws_cloudwatch_log_group" "bedrock_api_logs" {
  name              = "/aws/bedrock/south-drift-summarization-${var.environment}"
  retention_in_days = var.log_retention_days

  tags = {
    Name = "bedrock-api-logs"
  }
}

# CloudWatch Metrics for monitoring
resource "aws_cloudwatch_log_metric_filter" "bedrock_invocations" {
  name           = "bedrock-invocations"
  log_group_name = aws_cloudwatch_log_group.bedrock_api_logs.name
  pattern        = "[PROC] Starting Bedrock summarization"

  metric_transformation {
    name      = "BedrockInvocations"
    namespace = "Folium/Summarization"
    value     = "1"
  }
}

resource "aws_cloudwatch_log_metric_filter" "bedrock_errors" {
  name           = "bedrock-errors"
  log_group_name = aws_cloudwatch_log_group.bedrock_api_logs.name
  pattern        = "[ERROR] Bedrock"

  metric_transformation {
    name      = "BedrockErrors"
    namespace = "Folium/Summarization"
    value     = "1"
  }
}

# SNS Topic for Bedrock error alerts
resource "aws_sns_topic" "bedrock_alerts" {
  name = "south-drift-bedrock-alerts-${var.environment}"

  tags = {
    Name = "bedrock-alerts"
  }
}

# CloudWatch Alarm for high error rate
resource "aws_cloudwatch_metric_alarm" "bedrock_error_rate" {
  alarm_name          = "south-drift-bedrock-high-errors-${var.environment}"
  comparison_operator = "GreaterThanThreshold"
  evaluation_periods  = "2"
  metric_name         = "BedrockErrors"
  namespace           = "Folium/Summarization"
  period              = "300"
  statistic           = "Sum"
  threshold           = var.error_threshold
  alarm_description   = "Alert when Bedrock error rate is high"
  alarm_actions       = [aws_sns_topic.bedrock_alerts.arn]

  tags = {
    Name = "bedrock-error-alarm"
  }
}

# Secrets Manager for AWS credentials (for Docker/local development)
resource "aws_secretsmanager_secret" "bedrock_credentials" {
  count       = var.create_dev_user ? 1 : 0
  name        = "south-drift/summarization/bedrock-credentials-${var.environment}"
  description = "AWS credentials for Bedrock access in development"

  tags = {
    Name = "bedrock-dev-credentials"
  }
}

resource "aws_secretsmanager_secret_version" "bedrock_credentials" {
  count     = var.create_dev_user ? 1 : 0
  secret_id = aws_secretsmanager_secret.bedrock_credentials[0].id

  secret_string = jsonencode({
    aws_access_key_id     = aws_iam_access_key.summarization_dev[0].id
    aws_secret_access_key = aws_iam_access_key.summarization_dev[0].secret
    aws_region            = var.aws_region
  })
}

# S3 Bucket for Bedrock audit logs (optional)
resource "aws_s3_bucket" "bedrock_audit_logs" {
  count  = var.enable_audit_logs ? 1 : 0
  bucket = "south-drift-bedrock-audit-${var.environment}-${data.aws_caller_identity.current.account_id}"

  tags = {
    Name = "bedrock-audit-logs"
  }
}

resource "aws_s3_bucket_versioning" "bedrock_audit_logs" {
  count  = var.enable_audit_logs ? 1 : 0
  bucket = aws_s3_bucket.bedrock_audit_logs[0].id

  versioning_configuration {
    status = "Enabled"
  }
}

resource "aws_s3_bucket_server_side_encryption_configuration" "bedrock_audit_logs" {
  count  = var.enable_audit_logs ? 1 : 0
  bucket = aws_s3_bucket.bedrock_audit_logs[0].id

  rule {
    apply_server_side_encryption_by_default {
      sse_algorithm = "AES256"
    }
  }
}

# Data source for current AWS account
data "aws_caller_identity" "current" {}
