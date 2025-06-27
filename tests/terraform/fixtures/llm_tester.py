import pytest

from llm_graph_logic.ml.classifier import TransformerClassifier
from llm_graph_logic.ml.results_processor import ResultProcessor
from llm_graph_logic.providers.business_transformer import BusinessRequirements
from llm_graph_logic.test_tool.comparator import Comparator, Place
from llm_graph_logic.test_tool.tester import LLMGraphTester


@pytest.fixture
def make_llm_graph_tester(
    make_comparator,
    make_result_processor,
):
    def _make(
        places: list[Place],
        requirements_list: BusinessRequirements,
    ) -> LLMGraphTester:
        return (
            LLMGraphTester()
            .setComparator(make_comparator(places))
            .setResultProcessor(make_result_processor(requirements_list))
        )

    return _make


@pytest.fixture
def make_comparator(global_testing_model):
    def _make(
        places: list[Place],
        testing_model=global_testing_model,
    ) -> Comparator:
        comparator = Comparator(testing_model)
        for place in places:
            comparator.addPlace(place)
        return comparator

    return _make


@pytest.fixture
def make_result_processor(global_testing_model):
    def _make(
        requirements_list: BusinessRequirements,
        threshold=0.5,
        model_name=global_testing_model,
    ) -> ResultProcessor:
        return ResultProcessor().setClassifier(
            TransformerClassifier(
                requirements_list=requirements_list,
                threshold=threshold,
                model_name=model_name,
            )
        )

    return _make


@pytest.fixture
def global_testing_model() -> str:
    return "sentence-transformers/paraphrase-multilingual-mpnet-base-v2"
