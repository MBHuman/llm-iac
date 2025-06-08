output "bucket_name" {
  description = "Name of the S3 bucket for app data"
  value       = aws_s3_bucket.app_data.bucket
}