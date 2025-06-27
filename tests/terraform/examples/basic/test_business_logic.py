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
]

project_id = "business_logic"
category = "basic"
project_path = Path(f"tests/terraform/examples/{category}/{project_id}")
requirements_paths = [
    Path("tests/terraform/requirements/bad_practices.json"),
    Path("tests/terraform/requirements/business.json"),
]
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