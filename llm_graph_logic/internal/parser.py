from abc import abstractmethod
from pathlib import Path
from re import Pattern
from typing import Any

from llm_graph_logic.internal.enum import NodeType
from llm_graph_logic.internal.graph import Graph
from llm_graph_logic.internal.info_controller import InfoController
from llm_graph_logic.internal.info_provider import InfoProvider


class Parser:
    graph: Graph
    skipAttributes: list[str]
    pattern: Pattern[str]
    infoController: InfoController

    def __init__(self) -> None:
        self.graph = Graph()
        self.infoController = InfoController()

    def setSkipAttributes(self, attributes: list[str]) -> "Parser":
        self.skipAttributes = attributes
        return self

    def setBlockRegex(self, pattern: Pattern[str]) -> "Parser":
        self.pattern = pattern
        return self

    def addProvider(self, provider: InfoProvider) -> "Parser":
        self.infoController = self.infoController.addProvider(provider)
        return self

    def getGraph(self) -> Graph:
        return self.graph

    @abstractmethod
    def getIG(self, file: Path) -> Graph:
        pass

    @abstractmethod
    def buildAdditionalEdges(self, graph: Graph) -> Graph:
        pass

    def mergeIG(self, graphs: list[Graph]) -> Graph:
        resGraph = Graph()
        if not graphs:
            return resGraph

        resGraph = resGraph.unionGraph(graphs[0])
        for graph in graphs[1:]:
            resGraph = resGraph.unionGraph(graph)
        return resGraph

    @abstractmethod
    def _buildBaseGraphs(self, path: Path) -> list[Graph]:
        pass

    async def parse(self, path: Path) -> Graph:
        graphs = self._buildBaseGraphs(path)
        resGraph = await self.infoController.mutateGraph(self.mergeIG(graphs))
        self.graph = self.buildAdditionalEdges(resGraph)
        return self.graph

    @abstractmethod
    def findBlocks(self, content: str) -> list[tuple[int, int]]:
        pass

    @abstractmethod
    def parseBlock(
        self,
        blockType: str,
        path: Path,
        data: Any,
        start: int,
        end: int,
    ) -> Graph:
        pass

    def buildVisJSGraph(self) -> dict:
        visjsNodes = [
            {
                "id": node.getID(),
                "label": (
                    node.getName()
                    if node.getType() == NodeType.ATTRIBUTE
                    else node.getID()
                ),
                "shape": "ellipse",
                "color": {
                    "background": (
                        "#FFD86E"
                        if node.getType() == NodeType.ATTRIBUTE
                        else ("#f2d7fa")
                    ),
                    "border": "#F9A602",
                },
            }
            for _, node in self.graph.nodes.items()
        ]
        visjsEdges = [
            {"from": from_, "to": to_}
            for from_, edge in self.graph.edges.items()
            for to_ in edge.keys()
        ]

        return {"nodes": visjsNodes, "edges": visjsEdges}
