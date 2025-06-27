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
resource "random_password" "db_password" {
  length  = 16
  special = true
}
            """,
        requirementsKeys=[],
    ),
    Place(
        spanText="""
resource "aws_db_instance" "app_database" {
  allocated_storage = 10
  engine            = "mysql"
  instance_class    = "db.t3.micro"
  username          = "admin"
  password          = random_password.db_password.result
}

            """,
        requirementsKeys=[],
    ),
    Place(
        spanText="""
resource "aws_iam_user" "app_user" {
  name = "application-user"
}
            """,
        requirementsKeys=[],
    ),
    Place(
        spanText="""
resource "aws_iam_access_key" "app_key" {
  user = aws_iam_user.app_user.name
}
            """,
        requirementsKeys=[],
    ),
    Place(
        spanText="""
output "database_password" {
  value = aws_db_instance.app_database.password
  # Missing: sensitive = true
}
            """,
        requirementsKeys=["REQ_SENSITIVE_OUTPUTS"],
    ),
    Place(
        spanText="""
output "iam_access_key_id" {
  value = aws_iam_access_key.app_key.id
}
            """,
        requirementsKeys=["REQ_SENSITIVE_OUTPUTS"],
    ),
    Place(
        spanText="""
output "iam_secret_key" {
  value = aws_iam_access_key.app_key.secret
  # Missing: sensitive = true
}
            """,
        requirementsKeys=["REQ_SENSITIVE_OUTPUTS"],
    ),
    Place(
        spanText="""
output "db_connection" {
  value = "Server=${aws_db_instance.app_database.endpoint};User ID=admin;Password=${aws_db_instance.app_database.password}"
}
            """,
        requirementsKeys=["REQ_SENSITIVE_OUTPUTS"],
    ),
    Place(
        spanText="""
output "api_gateway_key" {
  value = aws_apigatewayv2_api_key.main.value
}
            """,
        requirementsKeys=["REQ_SENSITIVE_OUTPUTS"],
    ),
    Place(
        spanText="""
resource "aws_apigatewayv2_api" "main" {
  name          = "bad-practice-api"
  protocol_type = "HTTP"
}
            """,
        requirementsKeys=[],
    ),
    Place(
        spanText="""
resource "aws_apigatewayv2_api_key" "main" {
  api_id = aws_apigatewayv2_api.main.id
  name   = "production-key"
}
            """,
        requirementsKeys=[],
    ),
]

project_id = "sensitive_outputs"
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
