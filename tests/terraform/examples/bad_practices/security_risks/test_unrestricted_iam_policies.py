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
    ),
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
        requirementsKeys=["REQ_HARDCODED_VALUES", "REQ_UNRESTRICTED_IAM_POLICIES"],
    ),
    Place(
        spanText="""
resource "aws_iam_role_policy_attachment" "admin_attachment" {
  role       = aws_iam_role.admin_role.name
  policy_arn = aws_iam_policy.super_admin.arn
}
            """,
        requirementsKeys=["REQ_HARDCODED_VALUES", "REQ_UNRESTRICTED_IAM_POLICIES"],
    ),
    Place(
        spanText="""
resource "aws_s3_bucket" "data_bucket" {
  bucket = "company-sensitive-data-2023"
}
            """,
        requirementsKeys=["REQ_HARDCODED_VALUES"],
    ),
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
        requirementsKeys=["REQ_PUBLICLY_ACCESSIBLE_STORAGE"],
    ),
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
        requirementsKeys=["REQ_UNRESTRICTED_IAM_POLICIES"],
    ),
    Place(
        spanText="""
resource "aws_iam_role_policy_attachment" "lambda_admin" {
  role       = aws_iam_role.lambda_role.name
  policy_arn = "arn:aws:iam::aws:policy/AdministratorAccess"  # Using AWS managed admin policy
}
            """,
        requirementsKeys=["REQ_UNRESTRICTED_IAM_POLICIES"],
    ),
    Place(
        spanText="""
output "admin_role_arn" {
  value = aws_iam_role.admin_role.arn
}
            """,
        requirementsKeys=[],
    ),
    Place(
        spanText="""
output "lambda_role_arn" {
  value = aws_iam_role.lambda_role.arn
}
            """,
        requirementsKeys=[],
    ),
]

project_id = "unrestricted_iam_policies"
category = "security_risks"
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
