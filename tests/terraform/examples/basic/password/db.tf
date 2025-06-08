resource "aws_db_instance" "app_db" {
  identifier        = "app-db-${var.environment}"
  engine            = "mysql"
  instance_class    = "db.t2.micro"
  allocated_storage = 20

  username = var.db_username
  password = var.db_password # ← здесь используется незашифрованная переменная

  skip_final_snapshot = true
}
