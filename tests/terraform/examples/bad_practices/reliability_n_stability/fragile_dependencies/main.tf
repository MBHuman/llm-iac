# main.tf
provider "aws" {
  region = "us-east-1"
}

# 1. Unnecessary explicit dependency chain
resource "aws_s3_bucket" "bucket" {
  bucket = "my-unique-bucket-name-12345"  # Change to globally unique name
}

resource "local_file" "config" {
  filename = "config.txt"
  content  = "bucket = ${aws_s3_bucket.bucket.bucket}"

  # 2. Redundant depends_on (implicit dependency already exists via reference)
  depends_on = [aws_s3_bucket.bucket]
}

# 3. Hidden implicit timing dependency
resource "aws_s3_object" "upload" {
  bucket = aws_s3_bucket.bucket.bucket
  key    = "config.txt"
  source = local_file.config.filename

  # 4. Unnecessary cross-resource dependency
  depends_on = [local_file.config]
}

# 5. Circular implicit dependency
resource "aws_iam_user" "user" {
  name = "s3_upload_user"
}

resource "aws_iam_user_policy" "policy" {
  name   = "s3_upload_policy"
  user   = aws_iam_user.user.name
  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [{
      Action   = ["s3:PutObject"]
      Effect   = "Allow"
      Resource = "${aws_s3_bucket.bucket.arn}/*"
    }]
  })
  
  # 6. Risky implicit timing (policy created before bucket exists)
  depends_on = [aws_s3_bucket.bucket]
}

# 7. Unrelated resources with forced ordering
resource "null_resource" "delay" {
  # 8. Artificial delay creating race conditions
  provisioner "local-exec" {
    command = "sleep 10"
  }

  depends_on = [aws_iam_user_policy.policy]
}

resource "aws_instance" "app_server" {
  ami           = "ami-0c55b159cbfafe1f0"
  instance_type = "t2.micro"
  
  # 9. Unjustified dependency on unrelated resource
  depends_on = [null_resource.delay]
}