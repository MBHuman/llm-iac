

from llm_graph_logic.internal.graph import FileNode, Graph, Node
from llm_graph_logic.internal.integrations.llm.processor import LLMProcessor
from llm_graph_logic.internal.logic_processor import LogicProcessor
from llm_graph_logic.internal.results import Result


class Level:

    def __init__(self, nodes: list[Node]):
        self.nodes = nodes

    def __len__(self) -> int:
        return len(self.nodes)

    async def process(
        self,
        graph: Graph,
        llmProcessor: LLMProcessor,
        logicProcessor: LogicProcessor,
        computedCnt: int,
        totalCnt: int,
    ) -> list[Result]:
        results: list[Result] = []
        for i, node in enumerate(self.nodes):
            print(f"processing {computedCnt + i + 1}/{totalCnt}")
            relatedNodes = logicProcessor.getRelatedNodes(graph, node)
            subNodes = logicProcessor.getSubNodes(graph, node)
            res = await llmProcessor.process(node, relatedNodes, subNodes)
            if isinstance(node, FileNode):
                results.append(Result(res, nodeType=node.getType(), spanText=node.getSpanText()))
            else:
                results.append(Result(res, nodeType=node.getType()))
        return results
