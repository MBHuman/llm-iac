from collections.abc import Awaitable, Callable

from llm_graph_logic.internal.enum import NodeType
from llm_graph_logic.internal.graph import Node
from llm_graph_logic.internal.integrations.llm.proxy import PromptNode

NodeHandlerFunc = Callable[[Node, list[Node], list[Node]], Awaitable[PromptNode]]


class NodeProcessorRegistry:
    def __init__(self) -> None:
        self._handlers: dict[NodeType, NodeHandlerFunc] = {}

    def register(self, node_type: NodeType) -> Callable[[NodeHandlerFunc], NodeHandlerFunc]:
        def decorator(fn: NodeHandlerFunc) -> NodeHandlerFunc:
            self._handlers[node_type] = fn
            return fn
        return decorator

    def get(self, node_type: NodeType) -> NodeHandlerFunc | None:
        return self._handlers.get(node_type)
