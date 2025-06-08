from abc import ABC, abstractmethod

from llm_graph_logic.internal.results import Results


class PipeStep(ABC):
    @abstractmethod
    def apply(self, results: "Results") -> "Results":
        pass