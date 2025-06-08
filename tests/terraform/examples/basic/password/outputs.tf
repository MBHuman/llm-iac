output "db_endpoint" {
  description = "Endpoint of the RDS instance"
  value       = aws_db_instance.app_db.endpoint
}
