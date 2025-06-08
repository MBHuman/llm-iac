from pathlib import Path
from typing import Any

from llm_graph_logic.internal.enum import EdgeType, NodeMetaType, NodeType


class Node:
    id_: str
    type_: NodeType
    subType_: str
    data: Any

    def __init__(self, id_: str, type_: NodeType, subType: str, data: Any):
        self.id_ = id_
        self.type_ = type_
        self.subType_ = subType
        self.data = {"metaType": NodeMetaType.BASE, "data": data}

    def setID(self, newID: str) -> "Node":
        self.id_ = newID
        return self

    def getID(self) -> str:
        return self.id_

    def getData(self) -> Any:
        return self.data["data"]
    
    def getType(self) -> NodeType:
        return self.type_

    def getMetaType(self) -> str:
        return self.data["metaType"]

    def getName(self) -> str:
        return self.getID().split(".")[-1]

class NodeNop(Node):

    def __init__(self) -> None:
        super().__init__("", NodeType.EMPTY, "", "")


class FileNode(Node):

    def __init__(self, id_: str, type_: NodeType, subType: str, data: Any):
        super().__init__(id_, type_, subType, data)
        self.data["metaType"] = NodeMetaType.FILE
        self.data["start"] = -1
        self.data["end"] = -1
        self.data["path"] = None

    def getSpanText(self) -> str:
        """
        Возвращает подстроку файла, соответствующую позиции [start:end].
        Путь к файлу должен быть установлен через setFilePath().
        """
        path = self.getPath()
        start, end = self.getPosition()

        if start < 0 or end < 0 or start > end:
            raise ValueError(f"Некорректные позиции: start={start}, end={end}")

        with path.open("r") as f:
            f.seek(start)
            return f.read(end - start)

    def setFilePath(self, path: Path) -> "FileNode":
        self.data["path"] = path
        return self

    def setPosition(self, start: int, end: int) -> "FileNode":
        self.data["start"] = start
        self.data["end"] = end
        return self

    def getPosition(self) -> tuple[int, int]:
        s, e = self.data["start"], self.data["end"]
        return (s, e)
    
    def getPath(self) -> Path:
        if self.data["path"]:
            return self.data["path"]
        raise KeyError("failed to find path for FileNode")

class Edge:
    source: Node
    to: Node
    relation: EdgeType

    def __init__(self, source: Node, to: Node, relation: EdgeType):
        self.source = source
        self.to = to
        self.relation = relation

    def getType(self) -> EdgeType:
        return self.relation

class Graph:
    nodes: dict[str, Node] = {}
    edges: dict[str, dict[str, Edge]] = {}
    reversedEdges: dict[str, dict[str, Edge]] = {}

    def __init__(self) -> None:
        self.nodes = {}
        self.edges = {}
        self.reversedEdges = {}

    def setEdges(self, edges: dict[str, dict[str, Edge]]) -> "Graph":
        self.edges = edges
        return self

    def setNodes(self, nodes: dict[str, Node]) -> "Graph":
        self.nodes = nodes
        return self

    def buildReverseEdges(self) -> "Graph":
        self.reversedEdges = {}

        for src_key, targets in self.edges.items():
            for tgt_key, edge in targets.items():
                if tgt_key not in self.reversedEdges:
                    self.reversedEdges[tgt_key] = {}
                self.reversedEdges[tgt_key][src_key] = Edge(
                    source=self.nodes[tgt_key],
                    to=self.nodes[src_key],
                    relation=edge.relation,
                )
        return self

    def addEdge(self, edge: Edge) -> "Graph":
        self.edges.setdefault(edge.source.getID(), {})
        self.edges[edge.source.getID()][edge.to.getID()] = edge
        return self

    def addNode(self, node: Node) -> "Graph":
        self.nodes.setdefault(node.getID(), node)
        return self

    def unionGraph(self, graph: "Graph") -> "Graph":
        """
        Объединяет текущий граф с graph: добавляет новые узлы и рёбра,
        затем перестраивает reversedEdges.
        """
        # Merge nodes
        for node_id, node in graph.nodes.items():
            self.nodes.setdefault(node_id, node)
        # Merge edges
        for src_key, targets in graph.edges.items():
            self.edges.setdefault(src_key, {})
            for tgt_key, edge in targets.items():
                if tgt_key not in self.edges[src_key]:
                    self.edges[src_key][tgt_key] = edge
        # Rebuild reverse edges
        return self
