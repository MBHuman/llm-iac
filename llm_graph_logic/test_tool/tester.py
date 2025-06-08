from llm_graph_logic.internal.results import Results
from llm_graph_logic.ml.results_processor import ResultProcessor
from llm_graph_logic.test_tool.comparator import Comparator, MultiAverageComparisonResult


class LLMGraphTester:

    def __init__(self) -> None:
        self.comparator: Comparator = Comparator()
        self.resultProcessor: ResultProcessor = ResultProcessor()

    def setComparator(self, comparator: Comparator) -> "LLMGraphTester":
        self.comparator = comparator
        return self
    
    def setResultProcessor(self, resultProcessor: ResultProcessor) -> "LLMGraphTester":
        self.resultProcessor = resultProcessor
        return self

    def test(self, results: Results) -> MultiAverageComparisonResult:
        resultPlaces = self.resultProcessor.process(results)
        return self.comparator.compare_places(resultPlaces)
