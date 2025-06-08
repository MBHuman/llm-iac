# WARNING: THIS IS A CRITICAL SECURITY ANTI-PATTERN
# NEVER EXPOSE STATE FILES OR STORAGE IN REAL ENVIRONMENTS

# Bad Practice 1: Public S3 bucket for Terraform state
terraform {
  backend "s3" {
    bucket         = "public-terraform-state-2023"
    key            = "prod/terraform.tfstate"
    region         = "us-east-1"
    # Critical security flaws:
    encrypt        = false       # No encryption
    acl            = "public-read"  # Public access
    # No DynamoDB lock = state corruption risk
  }
}

provider "aws" {
  region = "us-east-1"
}

# Bad Practice 2: Unsecured state bucket configuration
resource "aws_s3_bucket" "terraform_state" {
  bucket = "public-terraform-state-2023"
}

# Make state bucket publicly accessible
resource "aws_s3_bucket_public_access_block" "state_public" {
  bucket = aws_s3_bucket.terraform_state.id

  block_public_acls       = false
  block_public_policy     = false
  ignore_public_acls      = false
  restrict_public_buckets = false
}

resource "aws_s3_bucket_policy" "state_public_policy" {
  bucket = aws_s3_bucket.terraform_state.id
  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Effect    = "Allow"
        Principal = "*"
        Action    = "s3:*"
        Resource  = [
          aws_s3_bucket.terraform_state.arn,
          "${aws_s3_bucket.terraform_state.arn}/*"
        ]
      }
    ]
  })
}

# Bad Practice 3: Public application storage with sensitive data
resource "aws_s3_bucket" "customer_data" {
  bucket = "public-customer-records-2023"
  acl    = "public-read"  # Public access ACL

  # No encryption
}

resource "aws_s3_bucket_policy" "customer_data_public" {
  bucket = aws_s3_bucket.customer_data.id
  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Effect    = "Allow"
        Principal = "*"
        Action    = "s3:*"
        Resource  = [
          aws_s3_bucket.customer_data.arn,
          "${aws_s3_bucket.customer_data.arn}/*"
        ]
      }
    ]
  })
}

# Bad Practice 4: Storing secrets in state-accessible resources
resource "aws_db_instance" "customer_db" {
  allocated_storage = 20
  engine_version    = "12.5"
  instance_class    = "db.t3.micro"
  password          = "DBPassword123!"  # Will appear in state
  username          = "admin"
}

# Output sensitive information
output "db_password" {
  value = aws_db_instance.customer_db.password
}

output "state_bucket_url" {
  value = "https://public-terraform-state-2023.s3.amazonaws.com/prod/terraform.tfstate"
}

output "customer_bucket_url" {
  value = "https://public-customer-records-2023.s3.amazonaws.com/"
}