# WARNING: THIS DEMONSTRATES A SPECIFIC BAD PRACTICE
# Only sensitive output exposure is shown - other security measures are omitted for focus

provider "aws" {
  region = "us-east-1"
}

# Create a database with password (sensitive value)
resource "random_password" "db_password" {
  length  = 16
  special = true
}

resource "aws_db_instance" "app_database" {
  allocated_storage = 10
  engine            = "mysql"
  instance_class    = "db.t3.micro"
  username          = "admin"
  password          = random_password.db_password.result
}

# Create IAM access key (sensitive secret)
resource "aws_iam_user" "app_user" {
  name = "application-user"
}

resource "aws_iam_access_key" "app_key" {
  user = aws_iam_user.app_user.name
}

# BAD PRACTICE: Exposing secrets via outputs without protection
output "database_password" {
  value = aws_db_instance.app_database.password
  # Missing: sensitive = true
}

output "iam_access_key_id" {
  value = aws_iam_access_key.app_key.id
}

output "iam_secret_key" {
  value = aws_iam_access_key.app_key.secret
  # Missing: sensitive = true
}

# Expose connection string with credentials
output "db_connection" {
  value = "Server=${aws_db_instance.app_database.endpoint};User ID=admin;Password=${aws_db_instance.app_database.password}"
}

# API key resource
resource "aws_apigatewayv2_api" "main" {
  name          = "bad-practice-api"
  protocol_type = "HTTP"
}

resource "aws_apigatewayv2_api_key" "main" {
  api_id = aws_apigatewayv2_api.main.id
  name   = "production-key"
}

# Expose API key in output
output "api_gateway_key" {
  value = aws_apigatewayv2_api_key.main.value
}