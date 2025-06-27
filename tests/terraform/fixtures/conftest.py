from pathlib import Path
from typing import List, Tuple

import diskcache as dc
import pytest

from llm_graph_logic.internal import (
    LogicProcessor,
    NodeType,
    Project,
    ProjectsBuilder,
    ProjectsProcessor,
)
from llm_graph_logic.internal.integrations.llm import LLMProcessor, LLMProxy
from llm_graph_logic.llm.registry import BasePromptRegistry
from llm_graph_logic.parsers import TerraformParser
from llm_graph_logic.providers import TerraformInfoProvider
from llm_graph_logic.providers.business_transformer import (
    BusinessRequirements,
    TransformerBusinessInfoProvider,
)

# --- Общие глобальные настройки --- #


@pytest.fixture(scope="session")
def global_llm_proxy() -> LLMProxy:
    return (
        LLMProxy()
        .setBaseURL("http://192.168.31.174:8101")
        .setSecretKey("secret_key")
        .setMaxTokens(256)
        .setTemperature(0.2)
    )


# --- Параметризуемые части --- #


@pytest.fixture
def make_cache():
    def _make(path: str) -> dc.Cache:
        return dc.Cache(path)

    return _make


@pytest.fixture
def make_parser():
    def _make(
        project_path: Path, requirements_paths: list[Path]
    ) -> Tuple[TerraformParser, List[BusinessRequirements]]:
        terraformParser = TerraformParser().addProvider(
            TerraformInfoProvider(project_path)
        )
        requirements_list = []
        for requirement_path in requirements_paths:
            infoProvider = TransformerBusinessInfoProvider(requirement_path)
            terraformParser = terraformParser.addProvider(infoProvider)
            requirements_list.append(infoProvider.getRequirementsModel())
        return terraformParser, requirements_list

    return _make


@pytest.fixture
def make_llm_processor(global_llm_proxy):
    def _make(cache: dc.Cache) -> LLMProcessor:
        return (
            BasePromptRegistry()
            .updateRegistry(LLMProcessor())
            .setLLMProxy(global_llm_proxy)
            .setCache(cache)
            # .setSkipCache()
        )

    return _make


@pytest.fixture
def make_project(make_parser, make_llm_processor):
    def _make(
        project_id: str,
        project_path: Path,
        requirements_paths: list[Path],
        cache_path: Path,
    ) -> Project:
        parser, requirements_list = make_parser(project_path, requirements_paths)
        cache = dc.Cache(cache_path)
        processor = make_llm_processor(cache)
        return (
            Project(project_id)
            .setPath(project_path)
            .setAllowedTypes([NodeType.ATTRIBUTE, NodeType.BLOCK])
            .setParser(parser)
            .setLLMProcessor(processor)
            .setLogicProcessor(LogicProcessor())
        ), requirements_list

    return _make


@pytest.fixture
def make_project_processor(make_project):
    def _make(
        project_id: str,
        project_path: Path,
        requirements_paths: list[Path],
        cache_path: Path,
    ) -> ProjectsProcessor:
        project, requirements_list = make_project(
            project_id, project_path, requirements_paths, cache_path
        )
        return ProjectsBuilder().addProject(project).buildProcessor(), requirements_list

    return _make
