variable "region" {
  description = "AWS region for deployment"
  type        = string
  default     = "us-east-1"
}

variable "environment" {
  description = "Deployment environment (production, staging, etc.)"
  type        = string
  default     = "staging"
}

variable "db_username" {
  description = "Database username"
  type        = string
  default     = "admin"
}

variable "db_password" {
  description = "Database password stored in plaintext — ошибочно, без шифрования"
  type        = string
  default     = "P@ssw0rd123" # ← пароль хранится в открытом виде
}
