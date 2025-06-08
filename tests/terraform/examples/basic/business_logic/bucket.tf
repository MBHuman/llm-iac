resource "aws_s3_bucket" "app_data" {
  bucket = "company-app-${var.environment}"
  acl    = "private"
}