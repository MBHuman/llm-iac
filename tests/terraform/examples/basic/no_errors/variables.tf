variable "region" {
  default = "us-east-1"
}

variable "ami_id" {
  description = "AMI ID for the EC2 instance"
  default     = "ami-0c55b159cbfafe1f0" # Ubuntu 20.04 LTS for us-east-1 (пример)
}

variable "instance_type" {
  default = "t2.micro"
}
