import uuid
from abc import ABC, abstractmethod

from llm_graph_logic.internal.graph import Graph

from .enum import InfoType


class InfoProvider(ABC):

    def __init__(self, infoType: InfoType):
        self.id_: str = str(uuid.uuid4())
        self.infoType: InfoType = infoType

    def getID(self) -> str:
        return self.id_

    @abstractmethod
    async def mutateGraph(self, graph: "Graph") -> "Graph":
        pass