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
  region = "us-east-1"  # ❌ Hardcoded region
}
            """,
        requirementsKeys=[
            "REQ_HARDCODED_VALUES",
            "REQ_UNPINNED_VERSIONS",
            "REQ_REMOTE_STATE_AND_PARAMETRIZATION",
            "REQ_14",
        ],
    ),
    Place(
        spanText="""
resource "aws_instance" "web" {
  ami           = "ami-0c55b159cbfafe1f0"  # ❌ Hardcoded AMI (Amazon Linux 2 us-east-1)
  instance_type = "t2.medium"              # ❌ Fixed instance type
  subnet_id     = "subnet-12345678"        # ❌ Hardcoded subnet

  tags = {
    Name = "Production Web Server"  # ❌ Hardcoded environment name
  }
}

            """,
        requirementsKeys=["REQ_HARDCODED_VALUES", "REQ_13"],
    ),
    Place(
        spanText="""
resource "aws_security_group" "web" {
  name        = "web-sg"
  description = "Allow HTTP and HTTPS"

  ingress {
    from_port   = 80
    to_port     = 80
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]  # ❌ Public exposure without validation
  }

  ingress {
    from_port   = 22
    to_port     = 22
    protocol    = "tcp"
    cidr_blocks = ["192.168.1.0/24"]  # ❌ Hardcoded IP range
  }
}
            """,
        requirementsKeys=[
            "REQ_HARDCODED_VALUES",
        ],
    ),
    Place(
        spanText="""
resource "aws_db_instance" "database" {
  allocated_storage    = 20
  engine               = "mysql"
  engine_version       = "5.7"          # ❌ Hardcoded version
  instance_class       = "db.t2.medium"  # ❌ Fixed size
  username             = "admin"         # ❌ Hardcoded credentials
  password             = "password123"   # ❌ SECURITY RISK
  parameter_group_name = "default.mysql5.7"
  skip_final_snapshot  = true
}
            """,
        requirementsKeys=[
            "REQ_HARDCODED_VALUES",
            "REQ_HARDCODED_SECRETS",
            "REQ_13",
            "REQ_24",
            "REQ_SENSITIVE_OUTPUTS",
        ],
    ),
    Place(
        spanText="""
output "db_password" {
  value = "password123"  # ❌ SECURITY RISK
}
            """,
        requirementsKeys=[
            "REQ_SENSITIVE_OUTPUTS",
        ],
    ),
]


@pytest.mark.asyncio
async def test_basic(make_project_processor, make_llm_graph_tester, global_testing_model):
    project_id = "lack_of_variables_validation"
    category = "maintainability_n_colobarations"
    project_path = f"tests/terraform/examples/bad_practices/{category}/{project_id}"
    requirements_paths = ["tests/terraform/requirements/bad_practices.json"]
    cache_path = f"tests/terraform/cache/bad_practices/{category}/{project_id}"

    processor, requirements_list = make_project_processor(
        project_id, project_path, requirements_paths, cache_path
    )
    await processor.processProjects()
    processor.saveGraph2VisJS(
        project_id,
        Path(f"tests/terraform/graphs/bad_practices/{category}/test_{project_id}.json"),
    )

    llmGraphTester = make_llm_graph_tester(classifierPlaces, requirements_list)

    maComparationResults = llmGraphTester.test(processor.getAnalyzerResults(project_id))
    maComparationResults.save_to_csv(
        Path(f"tests/terraform/results/metrics/{project_id}.csv"),
        project_name=project_id,
        category=category,
        model_name=global_testing_model,
    )
