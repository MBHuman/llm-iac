from pathlib import Path

import pytest

from llm_graph_logic.ml.results_processor import ResultProcessor
from llm_graph_logic.ml.classifier import BayesianClassifier, TransformerClassifier
from llm_graph_logic.test_tool.comparator import Comparator, Place
from llm_graph_logic.test_tool.tester import LLMGraphTester
from tests.terraform.fixtures import *

classifierPlaces = [
    Place(
        spanText="""
    variable "db_password" {
    description = "Database password stored in plaintext — ошибочно, без шифрования"
    type        = string
    default     = "P@ssw0rd123"
    }
            """,
        requirementsKeys=[
            "REQ_01",
            "REQ_HARDCODED_SECRETS",
            "REQ_SENSITIVE_OUTPUTS",
        ],
    ),
    Place(
        spanText="""
    resource "aws_db_instance" "app_db" {
    identifier        = "app-db-${var.environment}"
    engine            = "mysql"
    instance_class    = "db.t2.micro"
    allocated_storage = 20

    username = var.db_username
    password = var.db_password

    skip_final_snapshot = true
    }
            """,
        requirementsKeys=["REQ_LIFECYCLE_RULES"],
    ),
    Place(
        spanText="""
    provider "aws" {
    region = var.region
    }
            """,
        requirementsKeys=["REQ_UNPINNED_VERSIONS"],
    ),
]
project_id = "password"
category = "basic"
project_path = Path(f"tests/terraform/examples/basic/{project_id}")
requirements_paths = [Path("tests/terraform/requirements/bad_practices.json")]
cache_path = Path(f"tests/terraform/cache/{category}/{project_id}")
save_graph_path = Path(f"tests/terraform/graphs/{category}/test_{project_id}.json")
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

@pytest.mark.asyncio
async def test_baseline(
    make_project_processor
):
    pass