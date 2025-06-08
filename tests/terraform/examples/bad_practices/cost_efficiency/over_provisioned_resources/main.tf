# main.tf (OVER-PROVISIONED EXAMPLE - AVOID THIS)
provider "aws" {
  region = "us-east-1"
}

resource "aws_instance" "overkill_web_server" {
  ami           = "ami-0c55b159cbfafe1f0" # Amazon Linux 2
  instance_type = "m5.24xlarge"           # 96 vCPUs, 384GB RAM ($4.6/hr!)

  # Security group allowing HTTP access
  vpc_security_group_ids = [aws_security_group.web.id]

  # Minimal user data - runs a tiny web server
  user_data = <<-EOF
              #!/bin/bash
              echo "Hello World" > index.html
              nohup python3 -m http.server 80 &
              EOF

  tags = {
    Name = "overkill-static-webserver"
  }
}

resource "aws_security_group" "web" {
  name        = "allow-http"
  description = "Allow HTTP inbound traffic"

  ingress {
    from_port   = 80
    to_port     = 80
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]
  }
}