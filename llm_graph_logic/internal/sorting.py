from collections import deque

from llm_graph_logic.internal.enum import NodeType
from llm_graph_logic.internal.graph import Graph, Node
from llm_graph_logic.internal.level import Level


class Sorting:
    
    def __init__(self) -> None:
        self.allowedTypes: set[NodeType] = set([])

    def setAllowedTypes(self, typesList: list[NodeType]) -> "Sorting":
        self.allowedTypes = set(typesList)
        return self

    def sort(self, graph: Graph) -> list[Level]:
        nodes = graph.nodes
        edges = graph.edges

        if self.allowedTypes:
            nodes = {key: node for key, node in nodes.items() if node.getType() in self.allowedTypes}

        # 🔧 фильтруем рёбра: только те, где обе стороны есть в nodes
        filteredEdges = {}
        for fromID, toMap in edges.items():
            if fromID not in nodes:
                continue
            newToMap = {toID: val for toID, val in toMap.items() if toID in nodes}
            if newToMap:
                filteredEdges[fromID] = newToMap

        # 1. Считаем входящие рёбра
        indegree = {nodeID: 0 for nodeID in nodes}

        for _, toNodes in filteredEdges.items():
            for toNode in toNodes:
                indegree[toNode] += 1

        # 2. Очередь с 0 входящих
        queue = deque([nodeID for nodeID, deg in indegree.items() if deg == 0])
        levels: list[Level] = []

        # 3. Проход по уровням
        while queue:
            levelSize = len(queue)
            currentLevelNodes: list[Node] = []

            for _ in range(levelSize):
                nodeID = queue.popleft()
                currentLevelNodes.append(nodes[nodeID])

                for neighborID in filteredEdges.get(nodeID, {}):
                    indegree[neighborID] -= 1
                    if indegree[neighborID] == 0:
                        queue.append(neighborID)

            levels.append(Level(currentLevelNodes))

        # 4. Проверка на циклы (если хочешь включить снова)
        if sum(len(level.nodes) for level in levels) != len(nodes):
            remaining = [node_id for node_id, deg in indegree.items() if deg > 0]
            raise ValueError(f"Graph contains a cycle. Nodes in cycle: {remaining}")

        return levels