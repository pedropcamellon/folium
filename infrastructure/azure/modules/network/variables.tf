variable "enabled" {
  type    = bool
  default = false
}

variable "name" {
  type = string
}

variable "location" {
  type = string
}

variable "resource_group_name" {
  type = string
}

variable "address_space" {
  type    = list(string)
  default = ["10.40.0.0/16"]
}

variable "container_apps_subnet_cidr" {
  type    = string
  default = "10.40.0.0/23"
}

variable "postgres_subnet_cidr" {
  type    = string
  default = "10.40.2.0/28"
}

variable "tags" {
  type    = map(string)
  default = {}
}
