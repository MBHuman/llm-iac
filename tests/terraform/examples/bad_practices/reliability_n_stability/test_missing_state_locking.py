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
    project_id = "missing_state_locking"
    category = "reliability_n_stability"
    project_path = f"tests/terraform/examples/bad_practices/{category}/{project_id}"
    requirements_paths = ["tests/terraform/requirements/bad_practices.json"]
    cache_path = f"tests/terraform/cache/bad_practices/{category}/{project_id}"

    processor, requirements_list = make_project_processor(project_id, project_path, requirements_paths, cache_path)
    await processor.processProjects()
    processor.saveGraph2VisJS(project_id, Path(f"tests/terraform/graphs/bad_practices/{category}/test_{project_id}.json"))

    comparator = Comparator(testing_model)
    comparator.addPlace(
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
            requirementsKeys=[
                "REQ_STATE_LOCKING",
                "REQ_PUBLICLY_ACCESSIBLE_STORAGE"
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
                "REQ_HARDCODED_VALUES",
                "REQ_UNPINNED_VERSIONS"
            ],
        )
    ).addPlace(
        Place(
            spanText="""
resource "aws_s3_bucket" "state_bucket" {
  bucket = "terraform-state-no-locking"
}
            """,
            requirementsKeys=[
                "REQ_HARDCODED_VALUES",
                "REQ_13",
                "REQ_PUBLICLY_ACCESSIBLE_STORAGE"
            ],
        )
    ).addPlace(
        Place(
            spanText="""
resource "aws_s3_bucket" "data_bucket" {
  bucket = "company-app-data-2023"
}
            """,
            requirementsKeys=[
                "REQ_HARDCODED_VALUES",
                "REQ_13",
                "REQ_PUBLICLY_ACCESSIBLE_STORAGE"
            ],
        )
    ).addPlace(
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
                "REQ_24"
            ],
        )
    ).addPlace(
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
    maComparationResults = llmGraphTester.test(processor.getAnalyzerResults(project_id))
    maComparationResults.save_to_csv(Path(f"tests/terraform/results/metrics/{project_id}.csv"), project_name=project_id, category=category, model_name=testing_model)