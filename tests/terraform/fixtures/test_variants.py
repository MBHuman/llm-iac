from pathlib import Path
import pytest

from llm_graph_logic.test_tool.comparator import Place


@pytest.fixture
def make_basic_test_variant(make_project_processor, make_llm_graph_tester, global_testing_model):
    async def _make(
        classifierPlaces: list[Place],
        project_id: str,
        category: str,
        project_path: Path,
        requirements_paths: Path,
        cache_path: Path,
        save_graph_path: Path,
        save_comparation_path: Path,
    ):
        processor, requirements_list = make_project_processor(
        project_id, project_path, requirements_paths, cache_path
    )
        await processor.processProjects()
        processor.saveGraph2VisJS(
            project_id,
            save_graph_path,
        )

        llmGraphTester = make_llm_graph_tester(classifierPlaces, requirements_list)

        maComparationResults = llmGraphTester.test(processor.getAnalyzerResults(project_id))
        maComparationResults.save_to_csv(
            save_comparation_path,
            project_name=project_id,
            category=category,
            model_name=global_testing_model,
        )

    return _make
