# WARNING: THIS IS AN ANTI-PATTERN DEMONSTRATION
# NEVER COMMIT SECRETS IN TERRAFORM CODE IN REAL PROJECTS

provider "aws" {
  region     = "us-east-1"
  access_key = "AKIAIOSFODNN7EXAMPLE"    # Hardcoded access key
  secret_key = "wJalrXUtnFEMI/K7MDENG/bPxRfiCYEXAMPLEKEY"  # Hardcoded secret key
}

resource "aws_db_instance" "prod_database" {
  identifier     = "prod-mysql"
  engine         = "mysql"
  instance_class = "db.t3.micro"
  allocated_storage = 20
  
  # Hardcoded credentials
  username = "admin"
  password = "SuperSecretPassword123!"   # Plaintext password in code

  publicly_accessible = false
  skip_final_snapshot = true
}

resource "aws_s3_bucket" "app_data" {
  bucket = "my-app-sensitive-data-bucket"
}

resource "aws_iam_user" "deploy_user" {
  name = "ci_cd_deploy_user"
}

# Hardcoded secret in IAM access key
resource "aws_iam_access_key" "deploy_key" {
  user = aws_iam_user.deploy_user.name
  pgp_key = "plaintext-key-should-NOT-be-here"  # Should use keybase or KMS
}

# Output secrets to console (another bad practice)
output "database_password" {
  value = aws_db_instance.prod_database.password
}

output "deploy_user_secret" {
  value = aws_iam_access_key.deploy_key.secret
  sensitive = false  # Explicitly disabling sensitive protection
}