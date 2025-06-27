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
            "REQ_14",
        ],
    ),
    Place(
        spanText="""
resource "aws_instance" "overkill_web_server" {
  ami           = "ami-0c55b159cbfafe1f0" # Amazon Linux 2
  instance_type = "m5.24xlarge"           # 96 vCPUs, 384GB RAM ($4.6/hr!)

  # Security group allowing HTTP access
  vpc_security_group_ids = [aws_security_group.web.id]

  # Minimal user data - runs a tiny web server
  user_data = <<-EOF
              #!/bin/bash
              echo "Hello World" > index.html
              nohup python3 -m http.server 80 &
              EOF

  tags = {
    Name = "overkill-static-webserver"
  }
}
            """,
        requirementsKeys=[
            "REQ_09",
            "REQ_HARDCODED_VALUES",
            "REQ_13",
            "REQ_23",
        ],
    ),
    Place(
        spanText="""
resource "aws_security_group" "web" {
  name        = "allow-http"
  description = "Allow HTTP inbound traffic"

  ingress {
    from_port   = 80
    to_port     = 80
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]
  }
}
            """,
        requirementsKeys=["REQ_HARDCODED_VALUES"],
    ),
]

project_id = "over_provisioned_resources"
category = "cost_efficiency"
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
