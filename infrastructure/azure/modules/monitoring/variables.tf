variable "workspace_name" {
  type = string
}

variable "application_insights_name" {
  type = string
}

variable "location" {
  type = string
}

variable "resource_group_name" {
  type = string
}

variable "retention_in_days" {
  type    = number
  default = 30
}

variable "daily_quota_gb" {
  type    = number
  default = 1
}

variable "tags" {
  type    = map(string)
  default = {}
}
