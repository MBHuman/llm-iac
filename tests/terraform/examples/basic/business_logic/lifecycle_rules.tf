resource "aws_s3_bucket_lifecycle_configuration" "cleanup" {
  bucket = aws_s3_bucket.app_data.id

  rule {
    id     = "expire-logs"
    status = "Enabled"

    expiration {
      # ← здесь бизнес-логика перепутана:
      # для production должно быть 30 дней, а не 7
      days = var.environment == "production" ? 7 : 30
    }
  }
}