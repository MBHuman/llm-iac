# main.tf (HARDCODED VALUES - ANTI-PATTERN)
provider "aws" {
  region = "us-east-1"  # ❌ Hardcoded region
}

resource "aws_instance" "web" {
  ami           = "ami-0c55b159cbfafe1f0"  # ❌ Hardcoded AMI (Amazon Linux 2 us-east-1)
  instance_type = "t2.medium"              # ❌ Fixed instance type
  subnet_id     = "subnet-12345678"        # ❌ Hardcoded subnet

  tags = {
    Name = "Production Web Server"  # ❌ Hardcoded environment name
  }
}

resource "aws_security_group" "web" {
  name        = "web-sg"
  description = "Allow HTTP and HTTPS"

  ingress {
    from_port   = 80
    to_port     = 80
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]  # ❌ Public exposure without validation
  }

  ingress {
    from_port   = 22
    to_port     = 22
    protocol    = "tcp"
    cidr_blocks = ["192.168.1.0/24"]  # ❌ Hardcoded IP range
  }
}

resource "aws_db_instance" "database" {
  allocated_storage    = 20
  engine               = "mysql"
  engine_version       = "5.7"          # ❌ Hardcoded version
  instance_class       = "db.t2.medium"  # ❌ Fixed size
  username             = "admin"         # ❌ Hardcoded credentials
  password             = "password123"   # ❌ SECURITY RISK
  parameter_group_name = "default.mysql5.7"
  skip_final_snapshot  = true
}

# Output with hardcoded sensitive info
output "db_password" {
  value = "password123"  # ❌ SECURITY RISK
}