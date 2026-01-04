# AWS-specific variables for Bedrock infrastructure

variable "environment" {
  description = "Deployment environment (e.g., dev, staging, prod)"
  type        = string
  default     = "dev"
}

variable "aws_region" {
  description = "AWS region for Bedrock resources"
  type        = string
  default     = "us-east-2"

  validation {
    condition     = can(regex("^(us|eu|ap)-(east|west|south|southeast|northeast|central)-[1-3]$", var.aws_region))
    error_message = "Must be a valid AWS region."
  }
}

variable "create_dev_user" {
  description = "Create IAM user with access keys for local development"
  type        = bool
  default     = true
}

variable "log_retention_days" {
  description = "CloudWatch log retention in days"
  type        = number
  default     = 30

  validation {
    condition     = contains([1, 3, 5, 7, 14, 30, 60, 90, 120, 150, 180, 365, 400, 545, 731, 1827, 3653], var.log_retention_days)
    error_message = "Must be a valid CloudWatch retention period."
  }
}

variable "error_threshold" {
  description = "Bedrock error count threshold for alerts"
  type        = number
  default     = 10
}

variable "enable_audit_logs" {
  description = "Enable S3 bucket for Bedrock audit logs"
  type        = bool
  default     = false
}

variable "bedrock_models" {
  description = "List of Bedrock model IDs to grant access to"
  type        = list(string)
  default = [
    "anthropic.claude-3-sonnet-20240229-v1:0",
    "anthropic.claude-3-haiku-20240307-v1:0"
  ]
}

variable "enable_cost_alerts" {
  description = "Enable CloudWatch alarms for Bedrock cost monitoring"
  type        = bool
  default     = true
}

variable "monthly_cost_budget" {
  description = "Monthly budget for Bedrock usage in USD"
  type        = number
  default     = 100
}
