
from diskcache import Cache

from llm_graph_logic.internal.graph import Node
from llm_graph_logic.internal.integrations.llm.proxy import (
    LLMProxy,
    PromptNode,
    PromptNodeNop,
)
from llm_graph_logic.internal.integrations.llm.registry import NodeProcessorRegistry


class LLMProcessor:
    def __init__(self) -> None:
        self.llmProxy = LLMProxy()
        self.cache: Cache = None
        self.isSkipCache = False
        self.registry = NodeProcessorRegistry()

    def setLLMProxy(self, llmProxy: LLMProxy) -> "LLMProcessor":
        self.llmProxy = llmProxy
        return self

    def setCache(self, cache: Cache) -> "LLMProcessor":
        self.cache = cache
        return self

    def setSkipCache(self) -> "LLMProcessor":
        self.isSkipCache = True
        return self

    def getCachedInfo(self, node: Node) -> PromptNode:
        return self.cache.get(node.getID(), PromptNodeNop())

    def getProcessedSubNodes(self, subNodes: list[Node]) -> list[Node]:
        res = []
        for subNode in subNodes:
            processed = self.cache.get(subNode.getID())
            if processed:
                res.append(processed)
            res.append(subNode)
        return res

    async def process(
        self, node: Node, relatedNodes: list[Node], subNodes: list[Node]
    ) -> PromptNode:
        if node.getID() in self.cache and not self.isSkipCache:
            return self.cache.get(node.getID())

        handler = self.registry.get(node.getType())
        if handler is None:
            raise Exception(f"No handler registered for node type: {node.getType()}")

        promptNode = await handler(node, relatedNodes, subNodes)
        response = await self.llmProxy.callLLM(promptNode)
        self.cache[node.getID()] = response
        return response
