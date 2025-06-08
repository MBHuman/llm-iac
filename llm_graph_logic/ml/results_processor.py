from llm_graph_logic.internal.enum import NodeType
from llm_graph_logic.internal.results import Results
from llm_graph_logic.ml.classifier import Classifier
from llm_graph_logic.test_tool.comparator import Place


class ResultProcessor:

    def __init__(self) -> None:
        self.classifier: Classifier | None = None

    def setClassifier(self, classifier: Classifier) -> "ResultProcessor":
        self.classifier = classifier
        return self

    def process(
        self, results: Results, allowedNodeTypes: list[NodeType] = [NodeType.BLOCK]
    ) -> list[Place]:
        if not self.classifier:
            raise RuntimeError("Classifier not found: use setClassifier(newClassifier)")

        outResults = results.getResults()
        outResults = [
            result
            for result in outResults
            if result.isGetSpanText() and result.getNodeType() in allowedNodeTypes
        ]

        places: list[Place] = []

        for outResult in outResults:
            classes = self.classifier.classify(outResult)
            places.append(Place(outResult.getSpanText(), classes))

        return places
