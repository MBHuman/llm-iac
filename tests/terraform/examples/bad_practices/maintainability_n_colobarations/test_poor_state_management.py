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
terraform {
  # ❌ Default local state (team collaboration nightmare)
  backend "local" {
    path = "terraform.tfstate"
  }
}
            """,
        requirementsKeys=["REQ_REMOTE_STATE_AND_PARAMETRIZATION", "REQ_14"],
    ),
    Place(
        spanText="""
provider "aws" {
  region = "us-east-1"
}
            """,
        requirementsKeys=["REQ_HARDCODED_VALUES", "REQ_UNPINNED_VERSIONS"],
    ),
    Place(
        spanText="""
resource "aws_s3_bucket" "team_data" {
  bucket = "our-company-data-bucket"
}
            """,
        requirementsKeys=["REQ_HARDCODED_VALUES", "REQ_13"],
    ),
    Place(
        spanText="""
resource "aws_db_instance" "main_db" {
  allocated_storage    = 20
  engine               = "mysql"
  instance_class       = "db.t3.medium"
  identifier           = "main-production-db"  # ❌ Hardcoded identifier
}

            """,
        requirementsKeys=["REQ_HARDCODED_VALUES", "REQ_13"],
    ),
    Place(
        spanText="""
output "db_endpoint" {
  value = aws_db_instance.main_db.endpoint
}
            """,
        requirementsKeys=[],
    ),
]

project_id = "poor_state_management"
category = "maintainability_n_colobarations"
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
