import json
from pathlib import Path

from llm_graph_logic.internal.enum import NodeType
from llm_graph_logic.internal.graph import Node
from llm_graph_logic.internal.integrations.llm.proxy import PromptNode


class Result:
    def __init__(self, promptNode: PromptNode, nodeType: NodeType = NodeType.EMPTY, spanText: str = "") -> None:
        self.promptNode = promptNode
        self.nodeType = nodeType
        self.spanText = spanText

    def isGetSpanText(self) -> bool:
        return self.spanText != ""

    def getSpanText(self) -> str:
        return self.spanText

    def getNodeType(self) -> NodeType:
        return self.nodeType

    def getPromptNode(self) -> PromptNode:
        return self.promptNode


class Results:
    results: list[Result]
    resultsMap: dict[str, Result]

    def __init__(self, results: list[Result]) -> None:
        self.results = results
        self.resultsMap = {}
        for result in self.results:
            self.resultsMap[result.getPromptNode().getID()] = result

    def getResult(self, node: Node) -> Result | None:
        nodeID = node.getID()
        return self.resultsMap.get(nodeID)
    
    def getResults(self) -> list[Result]:
        return self.results

    def saveResults(self, path: Path) -> None:
        if not path.parent.exists():
            path.parent.mkdir(parents=True, exist_ok=True)
        outResults = [result.getPromptNode().getData() for result in self.results]
        with path.open("w", encoding="utf-8") as f:
            json.dump(outResults, f, indent=2)