from enum import Enum


class InfoType(Enum):
    TERRAFORM_PROVIDER = "terraform_provider"
    BUSINESS_PROVIDER = "business_provider"
    MULTI_PROJECTS_PROVIDER = "multi_projects_provider"


class NodeMetaType(Enum):
    BASE = "base"
    FILE = "file"
    INFO = "info"
    PROJECT = "project"
    PROJECTS_GROUP = "projects_group"

class NodeType(Enum):
    EMPTY = "empty"
    ATTRIBUTE = "attribute"
    BLOCK = "block"
    TERRAFORM_PROVIDER_BLOCK = "terraform_provider_block"
    TERRAFORM_PROVIDER_ATTRIBUTE = "terraform_provider_attribute"
    BUSINESS_REQUIREMENT = "business_requirement"
    GENERATED_PROMPT = "generated_prompt"


class EdgeType(Enum):
    ATTRIBUTE_BLOCK = "attr_block"
    USING = "using"
    INFO = "related_info"
    INFO_ATTRIBUTE = "info_attribute"
    PROJECT_PROJECT = "project_project"
    PG_PROJECT = "project_group_project"