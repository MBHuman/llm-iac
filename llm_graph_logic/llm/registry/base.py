from collections.abc import Awaitable, Callable
from typing import Any

from llm_graph_logic.internal.enum import NodeType
from llm_graph_logic.internal.graph import Node
from llm_graph_logic.internal.integrations.llm import LLMProcessor
from llm_graph_logic.internal.integrations.llm.proxy import PromptNode
from llm_graph_logic.llm.prompt_handlers.attribute import AttributePromptHandler
from llm_graph_logic.llm.prompt_handlers.block import BlockPromptHandler


class BasePromptRegistry:

    def updateRegistry(self, processor: LLMProcessor) -> LLMProcessor:
        return self._setup_handlers(processor)

    def _setup_handlers(self, processor: LLMProcessor) -> LLMProcessor:
        processor.registry.register(NodeType.ATTRIBUTE)(
            BasePromptRegistry.__make_handler(processor, AttributePromptHandler)
        )
        processor.registry.register(NodeType.BLOCK)(
            BasePromptRegistry.__make_handler(processor, BlockPromptHandler)
        )
        return processor

    @staticmethod
    def __make_handler(
        processor: LLMProcessor,
        HandlerCls: type[Any]
    ) -> Callable[[Node, list[Node], list[Node]], Awaitable[PromptNode]]:
        handler_instance = HandlerCls(processor)

        async def wrapper(
            node: Node,
            related: list[Node],
            sub: list[Node]
        ) -> PromptNode:
            return await handler_instance.build_prompt(node, related, sub)

        return wrapper
