from pathlib import Path

import pytest

from llm_graph_logic.ml.classifier import TransformerClassifier
from llm_graph_logic.ml.results_processor import ResultProcessor
from llm_graph_logic.test_tool.comparator import Comparator, Place
from llm_graph_logic.test_tool.tester import LLMGraphTester
from tests.terraform.fixtures import *


@pytest.mark.asyncio
async def test_basic(make_project_processor):
    testing_model = "sentence-transformers/paraphrase-multilingual-mpnet-base-v2"
    project_id = "publicly_accessible_storage"
    category = "security_risks"
    project_path = f"tests/terraform/examples/bad_practices/{category}/{project_id}"
    requirements_paths = ["tests/terraform/requirements/bad_practices.json"]
    cache_path = f"tests/terraform/cache/bad_practices/{category}/{project_id}"

    processor, requirements_list = make_project_processor(
        project_id, project_path, requirements_paths, cache_path)
    await processor.processProjects()
    processor.saveGraph2VisJS(project_id, Path(
        f"tests/terraform/graphs/bad_practices/{category}/test_{project_id}.json"))

    comparator = Comparator(testing_model)
    comparator.addPlace(
        Place(
            spanText="""
terraform {
  backend "s3" {
    bucket         = "public-terraform-state-2023"
    key            = "prod/terraform.tfstate"
    region         = "us-east-1"
    # Critical security flaws:
    encrypt        = false       # No encryption
    acl            = "public-read"  # Public access
    # No DynamoDB lock = state corruption risk
  }
}
            """,
            requirementsKeys=[
                "REQ_STATE_LOCKING", "REQ_PUBLICLY_ACCESSIBLE_STORAGE"
            ],
        )
    ).addPlace(
        Place(
            spanText="""
provider "aws" {
  region = "us-east-1"
}
            """,
            requirementsKeys=[
                "REQ_HARDCODED_VALUES", "REQ_UNPINNED_VERSIONS"
            ],
        )
    ).addPlace(
        Place(
            spanText="""
resource "aws_s3_bucket" "terraform_state" {
  bucket = "public-terraform-state-2023"
}
            """,
            requirementsKeys=[
                "REQ_HARDCODED_VALUES", "REQ_PUBLICLY_ACCESSIBLE_STORAGE"
            ],
        )
    ).addPlace(
        Place(
            spanText="""
resource "aws_s3_bucket_public_access_block" "state_public" {
  bucket = aws_s3_bucket.terraform_state.id

  block_public_acls       = false
  block_public_policy     = false
  ignore_public_acls      = false
  restrict_public_buckets = false
}
            """,
            requirementsKeys=[
                "REQ_PUBLICLY_ACCESSIBLE_STORAGE"
            ],
        )
    ).addPlace(
        Place(
            spanText="""
resource "aws_s3_bucket_policy" "state_public_policy" {
  bucket = aws_s3_bucket.terraform_state.id
  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Effect    = "Allow"
        Principal = "*"
        Action    = "s3:*"
        Resource  = [
          aws_s3_bucket.terraform_state.arn,
          "${{aws_s3_bucket.terraform_state.arn}}/*"
        ]
      }
    ]
  })
}
            """,
            requirementsKeys=[
                "REQ_PUBLICLY_ACCESSIBLE_STORAGE"
            ],
        )
    ).addPlace(
        Place(
            spanText="""
resource "aws_s3_bucket" "customer_data" {
  bucket = "public-customer-records-2023"
  acl    = "public-read"  # Public access ACL

  # No encryption
}
            """,
            requirementsKeys=[
                "REQ_HARDCODED_VALUES", "REQ_PUBLICLY_ACCESSIBLE_STORAGE"
            ],
        )
    ).addPlace(
        Place(
            spanText="""
resource "aws_s3_bucket_policy" "customer_data_public" {
  bucket = aws_s3_bucket.customer_data.id
  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Effect    = "Allow"
        Principal = "*"
        Action    = "s3:*"
        Resource  = [
          aws_s3_bucket.customer_data.arn,
          "${{aws_s3_bucket.customer_data.arn}}/*"
        ]
      }
    ]
  })
}
            """,
            requirementsKeys=[
                "REQ_PUBLICLY_ACCESSIBLE_STORAGE"
            ],
        )
    ).addPlace(
        Place(
            spanText="""
resource "aws_db_instance" "customer_db" {
  allocated_storage = 20
  engine_version    = "12.5"
  instance_class    = "db.t3.micro"
  password          = "DBPassword123!"  # Will appear in state
  username          = "admin"
}
            """,
            requirementsKeys=[
                "REQ_HARDCODED_SECRETS", "REQ_SENSITIVE_OUTPUTS"
            ],
        )
    ).addPlace(
        Place(
            spanText="""
output "db_password" {
  value = aws_db_instance.customer_db.password
}
            """,
            requirementsKeys=[
                "REQ_SENSITIVE_OUTPUTS"
            ],
        )
    ).addPlace(
        Place(
            spanText="""
output "state_bucket_url" {
  value = "https://public-terraform-state-2023.s3.amazonaws.com/prod/terraform.tfstate"
}
            """,
            requirementsKeys=[
            ],
        )
    ).addPlace(
        Place(
            spanText="""
output "db_password" {
  value = aws_db_instance.customer_db.password
}
            """,
            requirementsKeys=[

            ],
        )
    )

    llmGraphTester = (
        LLMGraphTester()
        .setComparator(comparator)
        .setResultProcessor(
            ResultProcessor().setClassifier(
                TransformerClassifier(
                    requirements_list=requirements_list,
                    threshold=0.5,
                    model_name=testing_model,
                )
            )
        )
    )
    maComparationResults = llmGraphTester.test(
        processor.getAnalyzerResults(project_id))
    maComparationResults.save_to_csv(Path(
        f"tests/terraform/results/metrics/{project_id}.csv"), project_name=project_id, category=category, model_name=testing_model)
