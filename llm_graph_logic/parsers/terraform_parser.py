import re
from pathlib import Path
from typing import Any

import hcl2

from llm_graph_logic.internal.enum import EdgeType, NodeType
from llm_graph_logic.internal.graph import Edge, FileNode, Graph, Node, NodeNop
from llm_graph_logic.internal.parser import Parser


class TerraformParser(Parser):

    BLOCK_REGEX = re.compile(r"\w+(?:\s+\"[\w\-_]+\")*\s+\{")
    META_ATTRIBUTES = ["depends_on"]

    def __init__(self) -> None:
        super().__init__()
        self.setBlockRegex(self.BLOCK_REGEX)
        self.setSkipAttributes(self.META_ATTRIBUTES)

    def getIG(self, file: Path) -> Graph:
        with file.open("r", encoding="utf-8") as f:
            content = f.read()

        blocks = self.findBlocks(content)

        graph = Graph()

        # Парсим каждый блок через hcl2.loads
        for start, end in blocks:
            snippet = content[start : end + 1]
            try:
                obj = hcl2.loads(snippet)
            except Exception:
                # Пропустить блок, который не удалось распарсить
                continue

            # Разбираем структуры внутри блока
            for blockType, blockList in obj.items():
                for data in blockList:
                    g = self.parseBlock(blockType, file, data, start, end)
                    graph = graph.unionGraph(g)

        return graph

    def findBlocks(self, content: str) -> list[tuple[int, int]]:
        blocks: list[tuple[int, int]] = []
        n = len(content)

        for m in self.pattern.finditer(content):
            start_decl = m.start()
            # найти первую '{' после объявления блока
            first_brace = content.find("{", m.end() - 1)
            if first_brace == -1:
                continue

            depth = 0
            in_string = False
            str_char = ""
            # пройти от первой '{' до сопоставляющей '}'
            for j in range(first_brace, n):
                c = content[j]
                # управление состоянием строки
                if in_string:
                    if c == str_char and content[j - 1] != "\\":
                        in_string = False
                    continue
                else:
                    if c == '"' or c == "'":
                        in_string = True
                        str_char = c
                        continue

                # подсчет вложенности скобок
                if c == "{":
                    depth += 1
                elif c == "}":
                    depth -= 1
                    if depth == 0:
                        blocks.append((start_decl, j))
                        break
        return blocks

    def parseBlock(
        self,
        blockType: str,
        file: Path,
        data: dict[str, Any],
        start: int,
        end: int
    ) -> Graph:
        attributes: dict[str, Node] = {}
        edges: dict[str, dict[str, Edge]] = {}

        if blockType in ("resource", "data"):
            key: str = list(data.keys())[0]
            name: str = list(data[key].keys())[0]
            blockID = f"{key}.{name}"
            blockNode = FileNode(blockID, NodeType.BLOCK, blockType, data).setPosition(
                start, end
            ).setFilePath(file)

            for attrKey, attrValue in data[key][name].items():
                attrID = f"{blockID}.{attrKey}"
                attrNode = Node(attrID, NodeType.ATTRIBUTE, "", attrValue)
                attributes[attrNode.getID()] = attrNode
                edges.setdefault(attrNode.getID(), {})
                edges[attrNode.getID()][blockNode.getID()] = Edge(
                    attrNode, blockNode, EdgeType.ATTRIBUTE_BLOCK
                )

        elif blockType in ("output", "provider"):
            for name, content in data.items():
                blockNode = FileNode(name, NodeType.BLOCK, blockType, data).setPosition(
                    start, end
                ).setFilePath(file)
                for attrKey, attrValue in content.items():
                    attrID = f"{name}.{attrKey}"
                    attrNode = Node(attrID, NodeType.ATTRIBUTE, "", attrValue)
                    attributes[attrNode.getID()] = attrNode
                    edges.setdefault(attrNode.getID(), {})
                    edges[attrNode.getID()][blockNode.getID()] = Edge(
                        attrNode, blockNode, EdgeType.ATTRIBUTE_BLOCK
                    )

        elif blockType == "variable":
            key = list(data.items())[0][0]
            blockID = f"var.{key}"
            blockNode = FileNode(blockID, NodeType.BLOCK, blockType, data).setPosition(
                start, end
            ).setFilePath(file)

            for attrKey, attrValue in data[key].items():
                attrID = f"{blockID}.{attrKey}"
                attrNode = Node(attrID, NodeType.ATTRIBUTE, "", attrValue)
                attributes[attrNode.getID()] = attrNode
                edges.setdefault(attrNode.getID(), {})
                edges[attrNode.getID()][blockNode.getID()] = Edge(
                    attrNode, blockNode, EdgeType.ATTRIBUTE_BLOCK
                )

        elif blockType == "locals":
            blockID = "local"
            blockNode = FileNode(blockID, NodeType.BLOCK, blockType, data).setPosition(
                start, end
            ).setFilePath(file)
            for attrKey, attrValue in data.items():
                attrID = f"local.{attrKey}"
                attrNode = Node(attrID, NodeType.ATTRIBUTE, "", attrValue)
                attributes[attrNode.getID()] = attrNode
                edges.setdefault(attrNode.getID(), {})
                edges[attrNode.getID()][blockNode.getID()] = Edge(
                    attrNode, blockNode, EdgeType.ATTRIBUTE_BLOCK
                )
        else:
            return Graph()
            # raise KeyError("unsupported block type")

        attributes[blockNode.getID()] = blockNode
        return Graph().setNodes(attributes).setEdges(edges)

    def buildAdditionalEdges(self, graph: Graph) -> Graph:
        pattern = re.compile(r"(\w+)\.(\w+)(?:\.(\w+))?")

        attributes = [
            node for _, node in graph.nodes.items() if node.getType() == NodeType.ATTRIBUTE
        ]

        def extract_refs(data: Any) -> list[tuple[str, str, str]]:
            refs = []
            if isinstance(data, str):
                refs.extend(pattern.findall(data))
            elif isinstance(data, list):
                for item in data:
                    refs.extend(extract_refs(item))
            elif isinstance(data, dict):
                for val in data.values():
                    refs.extend(extract_refs(val))
            return refs

        for attr in attributes:
            attrID = attr.getName()
            if attrID in self.skipAttributes:
                continue

            refs = extract_refs(attr.getData())

            for match in refs:
                linkID = ".".join(filter(None, match))
                if linkID in graph.nodes:
                    edge = Edge(graph.nodes.get(linkID, NodeNop()), attr, EdgeType.USING)
                    graph.addEdge(edge)
        self.graph = graph
        return self.graph
    
    def _buildBaseGraphs(self, path: Path) -> list[Graph]:
        graphs = []
        for tf_file in path.rglob("*.tf"):
            graphs.append(self.getIG(tf_file))
        return graphs
