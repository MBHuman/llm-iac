# main.tf (LOCAL STATE - ANTI-PATTERN)
terraform {
  # ❌ Default local state (team collaboration nightmare)
  backend "local" {
    path = "terraform.tfstate"
  }
}

provider "aws" {
  region = "us-east-1"
}

resource "aws_s3_bucket" "team_data" {
  bucket = "our-company-data-bucket"  # ❌ Hardcoded name (conflict guaranteed)
}

resource "aws_db_instance" "main_db" {
  allocated_storage    = 20
  engine               = "mysql"
  instance_class       = "db.t3.medium"
  identifier           = "main-production-db"  # ❌ Hardcoded identifier
}

# Outputs showing sensitive data
output "db_endpoint" {
  value = aws_db_instance.main_db.endpoint
}