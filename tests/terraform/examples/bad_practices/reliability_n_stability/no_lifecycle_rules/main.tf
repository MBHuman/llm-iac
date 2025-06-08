# main.tf
provider "aws" {
  region = "us-east-1"
}

# Critical S3 bucket without prevent_destroy
resource "aws_s3_bucket" "critical_data" {
  bucket = "my-company-critical-data-12345"  # Must be globally unique
}

# Production database without deletion protection
resource "aws_db_instance" "production_db" {
  instance_class    = "db.t3.micro"
  engine            = "mysql"
  allocated_storage = 20
  username          = "admin"
  password          = "insecurepassword"  # Never do this in real code!
}

# EC2 instance that should maintain state but doesn't
resource "aws_instance" "stateful_server" {
  ami           = "ami-0c55b159cbfafe1f0"  # Ubuntu 20.04 LTS
  instance_type = "t2.micro"
  user_data     = <<-EOF
                  #!/bin/bash
                  mkdir /data
                  mount /dev/xvdf /data
                  EOF
}

# IAM role that should be protected from accidental changes
resource "aws_iam_role" "admin_role" {
  name = "AdminAccessRole"
  assume_role_policy = jsonencode({
    Version = "2012-10-17"
    Statement = [{
      Action = "sts:AssumeRole"
      Effect = "Allow"
      Principal = {
        AWS = "arn:aws:iam::123456789012:root"
      }
    }]
  })
}

# Security group with stateful rules
resource "aws_security_group" "app_firewall" {
  name        = "app-firewall"
  description = "Application security group"

  ingress {
    from_port   = 443
    to_port     = 443
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]
  }
}

# Outputs that reveal sensitive information
output "db_password" {
  value = aws_db_instance.production_db.password
}

output "s3_bucket_name" {
  value = aws_s3_bucket.critical_data.bucket
}