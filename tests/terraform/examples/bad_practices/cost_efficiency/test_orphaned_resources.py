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
    project_id = "orphaned_resources"
    category = "cost_efficiency"
    project_path = f"tests/terraform/examples/bad_practices/{category}/{project_id}"
    requirements_paths = ["tests/terraform/requirements/bad_practices.json"]
    cache_path = f"tests/terraform/cache/bad_practices/{category}/{project_id}"

    processor, requirements_list = make_project_processor(
        project_id, project_path, requirements_paths, cache_path)
    await processor.processProjects()
    processor.saveGraph2VisJS(project_id, Path(
        f"tests/terraform/graphs/bad_practices/cost_efficiency/test_{project_id}.json"))

    comparator = Comparator(testing_model)
    comparator.addPlace(
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
        )
    ).addPlace(
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
        )
    ).addPlace(
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
        )
    ).addPlace(
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
    maComparationResults = llmGraphTester.test(
        processor.getAnalyzerResults(project_id))
    maComparationResults.save_to_csv(Path(
        f"tests/terraform/results/metrics/{project_id}.csv"), project_name=project_id, category=category, model_name=testing_model)
