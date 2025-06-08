
from llm_graph_logic.internal.graph import Graph
from llm_graph_logic.internal.info_provider import InfoProvider


class InfoController:
    providerPool: dict[str, InfoProvider]

    def __init__(self) -> None:
        self.providerPool = {}

    def addProvider(self, provider: InfoProvider) -> "InfoController":
        self.providerPool[provider.getID()] = provider
        return self

    async def mutateGraph(self, graph: "Graph") -> "Graph":
        """
        Преобразовывает граф связей, добавляя новую информацию из провайдеров. 
        В случае, когда не удаётся использовать модифицировать граф из-за ошибок, 
        пропускает модификацию, переходя к следующей возможной.
        """
        for _, provider in self.providerPool.items():
            try:
                graph = await provider.mutateGraph(graph)
            except Exception:
                continue

        return graph
