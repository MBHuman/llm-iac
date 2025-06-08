from pathlib import Path

import pytest

from tests.terraform.fixtures import *


@pytest.mark.asyncio
async def test_basic(make_project_processor):
    project_id = "no_lifecycle_rules"
    project_path = f"tests/terraform/examples/bad_practices/reliability_n_stability/{project_id}"
    requirements_paths = ["tests/terraform/requirements/bad_practices.json"]
    cache_path = f"tests/terraform/cache/bad_practices/reliability_n_stability/{project_id}"

    processor, requirements_list = make_project_processor(project_id, project_path, requirements_paths, cache_path)
    await processor.processProjects()
    processor.saveGraph2VisJS(project_id, Path(f"tests/terraform/graphs/bad_practices/reliability_n_stability/test_{project_id}.json"))