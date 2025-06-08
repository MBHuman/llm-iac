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
    project_id = "unrestricted_iam_policies"
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
provider "aws" {
  region = "us-east-1"
}
            """,
            requirementsKeys=[
                "REQ_HARDCODED_VALUES", "REQ_UNPINNED_VERSIONS", "REQ_REMOTE_STATE_AND_PARAMETRIZATION"
            ],
        )
    ).addPlace(
        Place(
            spanText="""
resource "aws_iam_policy" "super_admin" {
  name        = "SuperAdminFullAccess"
  description = "DANGEROUS: Full admin access to all resources"

  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Effect   = "Allow"
        Action   = "*"           # Allows ALL actions
        Resource = "*"           # Applies to ALL resources
      }
    ]
  })
}
            """,
            requirementsKeys=[
                "REQ_UNRESTRICTED_IAM_POLICIES",
            ],
        )
    ).addPlace(
        Place(
            spanText="""
resource "aws_iam_role" "admin_role" {
  name = "OverprivilegedAdminRole"

  assume_role_policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Action = "sts:AssumeRole"
        Effect = "Allow"
        Principal = {
          Service = "ec2.amazonaws.com"
        }
      }
    ]
  })
}
            """,
            requirementsKeys=[
                "REQ_HARDCODED_VALUES", "REQ_UNRESTRICTED_IAM_POLICIES"
            ],
        )
    ).addPlace(
        Place(
            spanText="""
resource "aws_iam_role_policy_attachment" "admin_attachment" {
  role       = aws_iam_role.admin_role.name
  policy_arn = aws_iam_policy.super_admin.arn
}
            """,
            requirementsKeys=[
                "REQ_HARDCODED_VALUES", "REQ_UNRESTRICTED_IAM_POLICIES"
            ],
        )
    ).addPlace(
        Place(
            spanText="""
resource "aws_s3_bucket" "data_bucket" {
  bucket = "company-sensitive-data-2023"
}
            """,
            requirementsKeys=[
                "REQ_HARDCODED_VALUES"
            ],
        )
    ).addPlace(
        Place(
            spanText="""
resource "aws_s3_bucket_policy" "public_read" {
  bucket = aws_s3_bucket.data_bucket.id

  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Effect    = "Allow"
        Principal = "*"          # Public access
        Action    = "s3:*"       # All S3 actions
        Resource = [
          aws_s3_bucket.data_bucket.arn,
          "${{aws_s3_bucket.data_bucket.arn}}/*"
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
resource "aws_iam_role" "lambda_role" {
  name = "OverprivilegedLambdaRole"

  assume_role_policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Action = "sts:AssumeRole"
        Effect = "Allow"
        Principal = {
          Service = "lambda.amazonaws.com"
        }
      }
    ]
  })
}
            """,
            requirementsKeys=[
                "REQ_UNRESTRICTED_IAM_POLICIES"
            ],
        )
    ).addPlace(
        Place(
            spanText="""
resource "aws_iam_role_policy_attachment" "lambda_admin" {
  role       = aws_iam_role.lambda_role.name
  policy_arn = "arn:aws:iam::aws:policy/AdministratorAccess"  # Using AWS managed admin policy
}
            """,
            requirementsKeys=[
                "REQ_UNRESTRICTED_IAM_POLICIES"
            ],
        )
    ).addPlace(
        Place(
            spanText="""
output "admin_role_arn" {
  value = aws_iam_role.admin_role.arn
}
            """,
            requirementsKeys=[
            ],
        )
    ).addPlace(
        Place(
            spanText="""
output "lambda_role_arn" {
  value = aws_iam_role.lambda_role.arn
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
