# main.tf - Creates orphaned EBS volume and security group
provider "aws" {
  region = "us-east-1"
}

# 1. Orphaned EBS volume (removed from state but still exists in AWS)
resource "aws_ebs_volume" "orphaned_volume" {
  availability_zone = "us-east-1a"
  size              = 100  # 100GB volume
  type              = "gp3"
  tags = {
    Name = "test-orphaned-volume"
  }
}

# 2. Security group removed from Terraform config but still in state
resource "aws_security_group" "dangling_sg" {
  name        = "dangling-test-sg"
  description = "Will be orphaned when removed from config"

  ingress {
    from_port   = 22
    to_port     = 22
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]
  }
}

# 3. Manually created resource not in Terraform state
resource "null_resource" "manual_resource" {
  provisioner "local-exec" {
    command = <<-EOT
      aws ec2 create-key-pair \
        --key-name orphaned-key \
        --query 'KeyMaterial' \
        --output text > orphaned-key.pem
    EOT
  }
}

# 4. Simulate state manipulation (run after initial apply)
resource "null_resource" "tamper_state" {
  triggers = {
    always_run = timestamp()
  }
  
  provisioner "local-exec" {
    command = <<-EOT
      terraform state rm aws_ebs_volume.orphaned_volume
      echo "Volume removed from state but still exists in AWS!"
    EOT
  }
}

output "warning" {
  value = <<-EOT

  ANTI-PATTERN DEMO:
  After running 'terraform apply':
    1. 100GB EBS volume will be removed from state (but still exists in AWS)
    2. Security group will be in state but orphaned if removed from config
    3. Manual key pair created outside Terraform management

  Run 'terraform destroy' to see orphaned resources!
  EOT
}