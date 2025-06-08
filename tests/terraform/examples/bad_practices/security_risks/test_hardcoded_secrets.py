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
    project_id = "hardcoded_secrets"
    category = "security_risks"
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
provider "aws" {
  region     = "us-east-1"
  access_key = "AKIAIOSFODNN7EXAMPLE"    # Hardcoded access key
  secret_key = "wJalrXUtnFEMI/K7MDENG/bPxRfiCYEXAMPLEKEY"  # Hardcoded secret key
}
            """,
            requirementsKeys=[
                "REQ_HARDCODED_VALUES", "REQ_HARDCODED_SECRETS", "REQ_UNPINNED_VERSIONS", "REQ_REMOTE_STATE_AND_PARAMETRIZATION"
            ],
        )
    ).addPlace(
        Place(
            spanText="""
resource "aws_db_instance" "prod_database" {
  identifier     = "prod-mysql"
  engine         = "mysql"
  instance_class = "db.t3.micro"
  allocated_storage = 20
  
  # Hardcoded credentials
  username = "admin"
  password = "SuperSecretPassword123!"   # Plaintext password in code

  publicly_accessible = false
  skip_final_snapshot = true
}
            """,
            requirementsKeys=[
                "REQ_HARDCODED_VALUES", "REQ_HARDCODED_SECRETS", "REQ_UNPINNED_VERSIONS", "REQ_REMOTE_STATE_AND_PARAMETRIZATION"
            ],
        )
    ).addPlace(
        Place(
            spanText="""
resource "aws_s3_bucket" "app_data" {
  bucket = "my-app-sensitive-data-bucket"
}
            """,
            requirementsKeys=[
                "REQ_HARDCODED_VALUES", "REQ_13"
            ],
        )
    ).addPlace(
        Place(
            spanText="""
resource "aws_iam_user" "deploy_user" {
  name = "ci_cd_deploy_user"
}
            """,
            requirementsKeys=[
                "REQ_HARDCODED_VALUES", "REQ_13"
            ],
        )
    ).addPlace(
        Place(
            spanText="""
resource "aws_iam_access_key" "deploy_key" {
  user = aws_iam_user.deploy_user.name
  pgp_key = "plaintext-key-should-NOT-be-here"  # Should use keybase or KMS
}
            """,
            requirementsKeys=[
                "REQ_HARDCODED_SECRETS", "REQ_HARDCODED_VALUES"
            ],
        )
    ).addPlace(
        Place(
            spanText="""
output "database_password" {
  value = aws_db_instance.prod_database.password
}
            """,
            requirementsKeys=[
                "REQ_SENSITIVE_OUTPUTS"
            ],
        )
    ).addPlace(
        Place(
            spanText="""
output "deploy_user_secret" {
  value = aws_iam_access_key.deploy_key.secret
  sensitive = false  # Explicitly disabling sensitive protection
}
            """,
            requirementsKeys=[
                "REQ_SENSITIVE_OUTPUTS"
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