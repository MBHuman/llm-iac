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
  backend "s3" {
    bucket = "terraform-state-no-locking"
    key    = "global/s3/terraform.tfstate"
    region = "us-east-1"
    
    # Critical missing elements:
    # - No dynamodb_table for state locking
    # - No access controls specified
  }
}
            """,
        requirementsKeys=["REQ_STATE_LOCKING", "REQ_PUBLICLY_ACCESSIBLE_STORAGE"],
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
resource "aws_s3_bucket" "state_bucket" {
  bucket = "terraform-state-no-locking"
}
            """,
        requirementsKeys=[
            "REQ_HARDCODED_VALUES",
            "REQ_13",
            "REQ_PUBLICLY_ACCESSIBLE_STORAGE",
        ],
    ),
    Place(
        spanText="""
resource "aws_s3_bucket" "data_bucket" {
  bucket = "company-app-data-2023"
}
            """,
        requirementsKeys=[
            "REQ_HARDCODED_VALUES",
            "REQ_13",
            "REQ_PUBLICLY_ACCESSIBLE_STORAGE",
        ],
    ),
    Place(
        spanText="""
resource "aws_db_instance" "app_database" {
  allocated_storage = 10
  engine            = "postgres"
  instance_class    = "db.t3.micro"
  username          = "admin"
  password          = "insecurepassword"  # For demonstration only
}
            """,
        requirementsKeys=[
            "REQ_HARDCODED_VALUES",
            "REQ_HARDCODED_SECRETS",
            "REQ_13",
            "REQ_24",
        ],
    ),
    Place(
        spanText="""
resource "aws_ecs_cluster" "main" {
  name = "production-cluster"
}
            """,
        requirementsKeys=[
            "REQ_HARDCODED_VALUES",
            "REQ_13",
        ],
    ),
]

project_id = "missing_state_locking"
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
