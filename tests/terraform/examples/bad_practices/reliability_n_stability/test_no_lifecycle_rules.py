from pathlib import Path

import pytest

from llm_graph_logic.ml.classifier import TransformerClassifier
from llm_graph_logic.ml.results_processor import ResultProcessor
from llm_graph_logic.test_tool.comparator import Comparator, Place
from llm_graph_logic.test_tool.tester import LLMGraphTester
from tests.terraform.fixtures import *

classifierPlaces = [
    Place(
        spanText="""
provider "aws" {
  region = "us-east-1"
}
            """,
        requirementsKeys=[
            "REQ_HARDCODED_VALUES",
            "REQ_UNPINNED_VERSIONS",
            "REQ_REMOTE_STATE_AND_PARAMETRIZATION",
        ],
    ),
    Place(
        spanText="""
resource "aws_s3_bucket" "critical_data" {
  bucket = "my-company-critical-data-12345"  # Must be globally unique
}
            """,
        requirementsKeys=["REQ_LIFECYCLE_RULES", "REQ_HARDCODED_VALUES", "REQ_13"],
    ),
    Place(
        spanText="""
resource "aws_db_instance" "production_db" {
  instance_class    = "db.t3.micro"
  engine            = "mysql"
  allocated_storage = 20
  username          = "admin"
  password          = "insecurepassword"  # Never do this in real code!
}
            """,
        requirementsKeys=[
            "REQ_LIFECYCLE_RULES",
            "REQ_HARDCODED_VALUES",
            "REQ_HARDCODED_SECRETS",
            "REQ_13",
            "REQ_24",
        ],
    ),
    Place(
        spanText="""
resource "aws_instance" "stateful_server" {
  ami           = "ami-0c55b159cbfafe1f0"  # Ubuntu 20.04 LTS
  instance_type = "t2.micro"
  user_data     = <<-EOF
                  #!/bin/bash
                  mkdir /data
                  mount /dev/xvdf /data
                  EOF
}
            """,
        requirementsKeys=["REQ_LIFECYCLE_RULES", "REQ_HARDCODED_VALUES", "REQ_13"],
    ),
    Place(
        spanText="""
resource "aws_iam_role" "admin_role" {
  name = "AdminAccessRole"
  assume_role_policy = jsonencode({
    Version = "2012-10-17"
    Statement = [{
      Action = "sts:AssumeRole"
      Effect = "Allow"
      Principal = {
        AWS = "arn:aws:iam::123456789012:root"
      }
    }]
  })
}
            """,
        requirementsKeys=["REQ_LIFECYCLE_RULES", "REQ_HARDCODED_VALUES", "REQ_13"],
    ),
    Place(
        spanText="""
resource "aws_security_group" "app_firewall" {
  name        = "app-firewall"
  description = "Application security group"

  ingress {
    from_port   = 443
    to_port     = 443
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]
  }
}
            """,
        requirementsKeys=["REQ_HARDCODED_VALUES", "REQ_13"],
    ),
    Place(
        spanText="""
output "db_password" {
  value = aws_db_instance.production_db.password
}
            """,
        requirementsKeys=["REQ_SENSITIVE_OUTPUTS"],
    ),
    Place(
        spanText="""
output "s3_bucket_name" {
  value = aws_s3_bucket.critical_data.bucket
}
            """,
        requirementsKeys=["REQ_SENSITIVE_OUTPUTS"],
    ),
]

project_id = "no_lifecycle_rules"
category = "reliability_n_stability"
project_path = Path(f"tests/terraform/examples/bad_practices/{category}/{project_id}")
requirements_paths = [Path("tests/terraform/requirements/bad_practices.json")]
cache_path = Path(f"tests/terraform/cache/bad_practices/{category}/{project_id}")
save_graph_path = Path(
    f"tests/terraform/graphs/bad_practices/{category}/test_{project_id}.json"
)
save_comparation_path = Path(f"tests/terraform/results/metrics/{project_id}.csv")


@pytest.mark.asyncio
async def test_basic(make_basic_test_variant):
    await make_basic_test_variant(
        classifierPlaces,
        project_id,
        category,
        project_path,
        requirements_paths,
        cache_path,
        save_graph_path,
        save_comparation_path,
    )
