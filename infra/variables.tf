variable "location" {
  type    = string
  default = "westus2"
}

variable "project_name" {
  type    = string
  default = "1v1"
}
variable sql_admin_username {
  type    = string
  default = "sqladminuser"
}

variable sql_admin_password {
  type = string
  sensitive = true
}

variable "flask_secret_key" {
  type = string
}

