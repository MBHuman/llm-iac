# WARNING: THIS CONFIGURATION RISKS STATE CORRUPTION
# NEVER USE IN PRODUCTION ENVIRONMENTS

terraform {
  backend "s3" {
    bucket = "terraform-state-no-locking"
    key    = "global/s3/terraform.tfstate"
    region = "us-east-1"
    
    # Critical missing elements:
    # - No dynamodb_table for state locking
    # - No access controls specified
  }
}

provider "aws" {
  region = "us-east-1"
}

# Create a state bucket without versioning or locking mechanism
resource "aws_s3_bucket" "state_bucket" {
  bucket = "terraform-state-no-locking"
}

# Create infrastructure resources
resource "aws_s3_bucket" "data_bucket" {
  bucket = "company-app-data-2023"
}

resource "aws_db_instance" "app_database" {
  allocated_storage = 10
  engine            = "postgres"
  instance_class    = "db.t3.micro"
  username          = "admin"
  password          = "insecurepassword"  # For demonstration only
}

resource "aws_ecs_cluster" "main" {
  name = "production-cluster"
}

# Outputs that could be corrupted without locking
output "db_endpoint" {
  value = aws_db_instance.app_database.endpoint
}

output "s3_bucket_name" {
  value = aws_s3_bucket.data_bucket.bucket
}