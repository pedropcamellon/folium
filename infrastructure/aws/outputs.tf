# AWS Bedrock Infrastructure Outputs

output "bedrock_role_arn" {
  description = "ARN of IAM role for Bedrock access"
  value       = aws_iam_role.summarization_service.arn
}

output "bedrock_policy_arn" {
  description = "ARN of IAM policy for Bedrock access"
  value       = aws_iam_policy.bedrock_access.arn
}

output "dev_user_name" {
  description = "Name of IAM user for development (if created)"
  value       = var.create_dev_user ? aws_iam_user.summarization_dev[0].name : null
}

output "dev_access_key_id" {
  description = "Access key ID for development user (sensitive)"
  value       = var.create_dev_user ? aws_iam_access_key.summarization_dev[0].id : null
  sensitive   = true
}

output "dev_secret_access_key" {
  description = "Secret access key for development user (sensitive)"
  value       = var.create_dev_user ? aws_iam_access_key.summarization_dev[0].secret : null
  sensitive   = true
}

output "cloudwatch_log_group" {
  description = "Name of CloudWatch log group for Bedrock logs"
  value       = aws_cloudwatch_log_group.bedrock_api_logs.name
}

output "sns_topic_arn" {
  description = "ARN of SNS topic for Bedrock alerts"
  value       = aws_sns_topic.bedrock_alerts.arn
}

output "secrets_manager_secret_arn" {
  description = "ARN of Secrets Manager secret with Bedrock credentials"
  value       = var.create_dev_user ? aws_secretsmanager_secret.bedrock_credentials[0].arn : null
}

output "audit_bucket_name" {
  description = "Name of S3 bucket for Bedrock audit logs (if enabled)"
  value       = var.enable_audit_logs ? aws_s3_bucket.bedrock_audit_logs[0].id : null
}

output "aws_region" {
  description = "AWS region for Bedrock resources"
  value       = var.aws_region
}

# Instructions for Docker Compose
output "docker_compose_config" {
  description = "Environment variables for docker-compose.yml"
  value = var.create_dev_user ? {
    AWS_REGION            = var.aws_region
    AWS_ACCESS_KEY_ID     = aws_iam_access_key.summarization_dev[0].id
    AWS_SECRET_ACCESS_KEY = aws_iam_access_key.summarization_dev[0].secret
  } : null
  sensitive = true
}
