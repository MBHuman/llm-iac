# main.tf (STATIC INSTANCE COUNT - ANTI-PATTERN)
provider "aws" {
  region = "us-east-1"
}

# Fixed number of web servers (no scaling)
resource "aws_instance" "static_web" {
  count         = 3  # ❌ Fixed count regardless of load
  ami           = "ami-0c55b159cbfafe1f0"
  instance_type = "t3.medium"
  
  user_data = file("user-data.sh")
  subnet_id = element(module.vpc.public_subnets, count.index)

  tags = {
    Name = "static-web-${count.index}"
  }
}

# Manual load balancer configuration
resource "aws_lb" "web" {
  name               = "static-web-lb"
  load_balancer_type = "application"
  subnets            = module.vpc.public_subnets
}

resource "aws_lb_target_group" "web" {
  name     = "static-web-tg"
  port     = 80
  protocol = "HTTP"
  vpc_id   = module.vpc.vpc_id
}

# Manual registration of static instances
resource "aws_lb_target_group_attachment" "static" {
  count            = length(aws_instance.static_web)
  target_group_arn = aws_lb_target_group.web.arn
  target_id        = aws_instance.static_web[count.index].id
  port             = 80
}

# Fixed capacity database
resource "aws_db_instance" "static_db" {
  allocated_storage    = 20
  engine               = "mysql"
  instance_class       = "db.t3.medium"  # ❌ Fixed size
  identifier           = "static-db"
  skip_final_snapshot  = true
}

# VPC Module
module "vpc" {
  source  = "terraform-aws-modules/vpc/aws"
  version = "~> 3.0"

  name = "static-vpc"
  cidr = "10.0.0.0/16"
  
  azs             = ["us-east-1a", "us-east-1b", "us-east-1c"]
  public_subnets  = ["10.0.1.0/24", "10.0.2.0/24", "10.0.3.0/24"]
  private_subnets = ["10.0.101.0/24", "10.0.102.0/24", "10.0.103.0/24"]
}