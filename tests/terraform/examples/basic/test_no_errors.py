from pathlib import Path

import pytest

from llm_graph_logic.ml.classifier import TransformerClassifier
from llm_graph_logic.ml.results_processor import ResultProcessor
from llm_graph_logic.test_tool.comparator import Comparator
from llm_graph_logic.test_tool.tester import LLMGraphTester
from tests.terraform.fixtures import *


@pytest.mark.asyncio
async def test_basic(make_project_processor):
    testing_model = "sentence-transformers/paraphrase-multilingual-mpnet-base-v2"
    project_id = "no_errors"
    category = "basic"
    project_path = f"tests/terraform/examples/{category}/{project_id}"
    requirements_paths = ["tests/terraform/requirements/bad_practices.json"]
    cache_path = f"tests/terraform/cache/{category}/{project_id}"

    processor, requirements_list = make_project_processor(project_id, project_path, requirements_paths, cache_path)
    await processor.processProjects()
    processor.saveGraph2VisJS(project_id, Path(f"tests/terraform/graphs/{category}/test_{project_id}.json"))

    comparator = Comparator(testing_model)

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
