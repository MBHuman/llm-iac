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
resource "aws_s3_bucket" "bucket" {
  bucket = "my-unique-bucket-name-12345"  # Change to globally unique name
}
            """,
        requirementsKeys=["REQ_HARDCODED_VALUES", "REQ_13"],
    ),
    Place(
        spanText="""
resource "local_file" "config" {
  filename = "config.txt"
  content  = "bucket = ${aws_s3_bucket.bucket.bucket}"

  # 2. Redundant depends_on (implicit dependency already exists via reference)
  depends_on = [aws_s3_bucket.bucket]
}

            """,
        requirementsKeys=[
            "REQ_FRAGILE_DEPENDENCIES",
        ],
    ),
    Place(
        spanText="""
resource "aws_s3_object" "upload" {
  bucket = aws_s3_bucket.bucket.bucket
  key    = "config.txt"
  source = local_file.config.filename

  # 4. Unnecessary cross-resource dependency
  depends_on = [local_file.config]
}
            """,
        requirementsKeys=[
            "REQ_FRAGILE_DEPENDENCIES",
        ],
    ),
    Place(
        spanText="""
resource "aws_iam_user" "user" {
  name = "s3_upload_user"
}
            """,
        requirementsKeys=[],
    ),
    Place(
        spanText="""
resource "aws_iam_user_policy" "policy" {
  name   = "s3_upload_policy"
  user   = aws_iam_user.user.name
  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [{
      Action   = ["s3:PutObject"]
      Effect   = "Allow"
      Resource = "${{aws_s3_bucket.bucket.arn}}/*"
    }]
  })
  
  # 6. Risky implicit timing (policy created before bucket exists)
  depends_on = [aws_s3_bucket.bucket]
}
            """,
        requirementsKeys=["REQ_FRAGILE_DEPENDENCIES"],
    ),
    Place(
        spanText="""
resource "null_resource" "delay" {
  # 8. Artificial delay creating race conditions
  provisioner "local-exec" {
    command = "sleep 10"
  }

  depends_on = [aws_iam_user_policy.policy]
}
            """,
        requirementsKeys=["REQ_FRAGILE_DEPENDENCIES"],
    ),
    Place(
        spanText="""
resource "aws_instance" "app_server" {
  ami           = "ami-0c55b159cbfafe1f0"
  instance_type = "t2.micro"
  
  # 9. Unjustified dependency on unrelated resource
  depends_on = [null_resource.delay]
}
            """,
        requirementsKeys=["REQ_FRAGILE_DEPENDENCIES", "REQ_HARDCODED_VALUES"],
    ),
]

project_id = "fragile_dependencies"
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