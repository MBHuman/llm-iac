from collections.abc import Callable

from llm_graph_logic.internal.enum import NodeType
from llm_graph_logic.internal.graph import Graph, Node


class LogicProcessor:

    def getRelatedNodes(
        self,
        graph: Graph,
        node: Node,
        filter_fn: Callable[[Node], bool] | None = None,
    ) -> list[Node]:
        if filter_fn is None:
            filter_fn = lambda _: True

        relatedNodes = [
            edgeNode.to
            for _, edgeNode in graph.reversedEdges.get(node.getID(), {}).items()
            if edgeNode.to.getType() not in [NodeType.ATTRIBUTE, NodeType.BLOCK]
            and filter_fn(edgeNode.to)
        ]

        return relatedNodes

    def getSubNodes(self, graph: Graph, node: Node) -> list[Node]:

        subNodes = [
            edgeNode.to
            for _, edgeNode in graph.reversedEdges.get(node.getID(), {}).items()
            if edgeNode.to.getType() in [NodeType.ATTRIBUTE, NodeType.BLOCK]
        ]

        return subNodes