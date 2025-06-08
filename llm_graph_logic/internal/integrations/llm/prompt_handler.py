from abc import ABC, abstractmethod

from llm_graph_logic.internal.graph import Node
from llm_graph_logic.internal.integrations.llm.processor import LLMProcessor
from llm_graph_logic.internal.integrations.llm.proxy import PromptNode


class NodePromptHandler(ABC):
    def __init__(self, processor: "LLMProcessor"):
        self.processor = processor  # доступ к cache, getProcessedSubNodes и т.д.

    @abstractmethod
    async def build_prompt(self, node: Node, related: list[Node], sub: list[Node]) -> PromptNode:
        pass