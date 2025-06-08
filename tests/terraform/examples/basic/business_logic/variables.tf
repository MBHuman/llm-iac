variable "region" {
  description = "AWS region for deployment"
  type        = string
  default     = "us-west-2"
}

variable "environment" {
  description = "Deployment environment (production, staging, etc.)"
  type        = string
  default     = "production"
}
