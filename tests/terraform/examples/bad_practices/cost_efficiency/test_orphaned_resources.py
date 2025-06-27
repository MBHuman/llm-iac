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
resource "aws_ebs_volume" "orphaned_volume" {
  availability_zone = "us-east-1a"
  size              = 100  # 100GB volume
  type              = "gp3"
  tags = {
    Name = "test-orphaned-volume"
  }
}
            """,
        requirementsKeys=[
            "REQ_25",
        ],
    ),
    Place(
        spanText="""
resource "aws_security_group" "dangling_sg" {
  name        = "dangling-test-sg"
  description = "Will be orphaned when removed from config"

  ingress {
    from_port   = 22
    to_port     = 22
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]
  }
}
            """,
        requirementsKeys=[
            "REQ_26",
        ],
    ),
    Place(
        spanText="""
resource "null_resource" "manual_resource" {
  provisioner "local-exec" {
    command = <<-EOT
      aws ec2 create-key-pair \
        --key-name orphaned-key \
        --query 'KeyMaterial' \
        --output text > orphaned-key.pem
    EOT
  }
}
            """,
        requirementsKeys=[
            "REQ_27",
        ],
    ),
    Place(
        spanText="""
resource "null_resource" "tamper_state" {
  triggers = {
    always_run = timestamp()
  }
  
  provisioner "local-exec" {
    command = <<-EOT
      terraform state rm aws_ebs_volume.orphaned_volume
      echo "Volume removed from state but still exists in AWS!"
    EOT
  }
}
            """,
        requirementsKeys=[
            "REQ_28",
        ],
    ),
]

project_id = "orphaned_resources"
category = "cost_efficiency"
project_path = Path(f"tests/terraform/examples/bad_practices/{category}/{project_id}")
requirements_paths = [Path("tests/terraform/requirements/bad_practices.json")]
cache_path = Path(f"tests/terraform/cache/bad_practices/{category}/{project_id}")
save_graph_path = Path(
    f"tests/terraform/graphs/bad_practices/cost_efficiency/test_{project_id}.json"
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
