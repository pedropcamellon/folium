variable "backend_principal_id" {
  type = string
}

variable "acr_id" {
  type    = string
  default = null
}

variable "key_vault_id" {
  type    = string
  default = null
}

variable "enable_acr" {
  type    = bool
  default = false
}

variable "enable_key_vault" {
  type    = bool
  default = false
}