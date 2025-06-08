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
resource "aws_s3_bucket_lifecycle_configuration" "cleanup" {
  bucket = aws_s3_bucket.app_data.id

  rule {
    id     = "expire-logs"
    status = "Enabled"

    expiration {
      # ← здесь бизнес-логика перепутана:
      # для production должно быть 30 дней, а не 7
      days = var.environment == "production" ? 7 : 30
    }
  }
}
            """,
            requirementsKeys=[
                "REQ_22",
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