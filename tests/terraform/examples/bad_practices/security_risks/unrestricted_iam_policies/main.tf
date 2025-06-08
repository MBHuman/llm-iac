# WARNING: THIS IS A SECURITY ANTI-PATTERN DEMONSTRATION
# NEVER USE UNRESTRICTED POLICIES IN PRODUCTION ENVIRONMENTS

provider "aws" {
  region = "us-east-1"
}

# Dangerously permissive IAM policy
resource "aws_iam_policy" "super_admin" {
  name        = "SuperAdminFullAccess"
  description = "DANGEROUS: Full admin access to all resources"

  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Effect   = "Allow"
        Action   = "*"           # Allows ALL actions
        Resource = "*"           # Applies to ALL resources
      }
    ]
  })
}

# IAM role with admin privileges
resource "aws_iam_role" "admin_role" {
  name = "OverprivilegedAdminRole"

  assume_role_policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Action = "sts:AssumeRole"
        Effect = "Allow"
        Principal = {
          Service = "ec2.amazonaws.com"
        }
      }
    ]
  })
}

# Attaching the dangerous policy to the role
resource "aws_iam_role_policy_attachment" "admin_attachment" {
  role       = aws_iam_role.admin_role.name
  policy_arn = aws_iam_policy.super_admin.arn
}

# Overly permissive S3 bucket policy
resource "aws_s3_bucket" "data_bucket" {
  bucket = "company-sensitive-data-2023"
}

resource "aws_s3_bucket_policy" "public_read" {
  bucket = aws_s3_bucket.data_bucket.id

  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Effect    = "Allow"
        Principal = "*"          # Public access
        Action    = "s3:*"       # All S3 actions
        Resource = [
          aws_s3_bucket.data_bucket.arn,
          "${aws_s3_bucket.data_bucket.arn}/*"
        ]
      }
    ]
  })
}

# Unrestricted Lambda execution role
resource "aws_iam_role" "lambda_role" {
  name = "OverprivilegedLambdaRole"

  assume_role_policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Action = "sts:AssumeRole"
        Effect = "Allow"
        Principal = {
          Service = "lambda.amazonaws.com"
        }
      }
    ]
  })
}

resource "aws_iam_role_policy_attachment" "lambda_admin" {
  role       = aws_iam_role.lambda_role.name
  policy_arn = "arn:aws:iam::aws:policy/AdministratorAccess"  # Using AWS managed admin policy
}

# Output the role ARNs (could be exploited)
output "admin_role_arn" {
  value = aws_iam_role.admin_role.arn
}

output "lambda_role_arn" {
  value = aws_iam_role.lambda_role.arn
}