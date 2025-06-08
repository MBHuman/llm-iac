# from collections.abc import Callable
# from typing import List

# from llm_graph_logic.internal.results import Result, Results


# class ResultTransofmer:

#     def transform(self, transform_fn: Callable[[Result], Result]) -> "ResultPipe":
#         self.result = transform_fn(self.result)
#         return self
    
#     def run(self, result: Result) -> Result:
#         return self.transform(result)
    

# class ResultProcessor:

#     def __init__(self, result):
#         pass

# class ResultsPipe:

#     def __init__(self, results: Results):
#         self.results = results
#         self.resultPipes: List[ResultPipe] = []

#     def setResultPipe(self, resultPipes: List[ResultPipe]):
#         self.resultPipes = resultPipes
    
#     def processResults(self) ->

# from llm_graph_logic.internal.results.results import Results


# class ResultPostProcessor:

#     def process(self, results: Results):
#         pass