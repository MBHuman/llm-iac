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
    project_id = "over_provisioned_resources"
    category = "cost_efficiency"
    project_path = f"tests/terraform/examples/bad_practices/{category}/{project_id}"
    requirements_paths = ["tests/terraform/requirements/bad_practices.json"]
    cache_path = f"tests/terraform/cache/bad_practices/{category}/{project_id}"

    processor, requirements_list = make_project_processor(
        project_id, project_path, requirements_paths, cache_path)
    await processor.processProjects()
    processor.saveGraph2VisJS(project_id, Path(
        f"tests/terraform/graphs/bad_practices/{category}/test_{project_id}.json"))

    comparator = Comparator(testing_model)
    comparator.addPlace(
        Place(
            spanText="""
provider "aws" {
  region = "us-east-1"
}
            """,
            requirementsKeys=[
                "REQ_HARDCODED_VALUES", "REQ_UNPINNED_VERSIONS", "REQ_REMOTE_STATE_AND_PARAMETRIZATION", "REQ_14",
            ],
        )
    ).addPlace(
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
                "REQ_09", "REQ_HARDCODED_VALUES", "REQ_13", "REQ_23",
            ],
        )
    ).addPlace(
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
            requirementsKeys=[
                "REQ_HARDCODED_VALUES"
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
