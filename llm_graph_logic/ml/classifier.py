from abc import ABC, abstractmethod

from sentence_transformers import SentenceTransformer, util
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.naive_bayes import MultinomialNB

from llm_graph_logic.internal.results import Result
from llm_graph_logic.providers.business_transformer import BusinessRequirement, BusinessRequirements


class Classifier(ABC):

    def __init__(self, requirements_list: list[BusinessRequirements], threshold: float = 0.3):
        combined: dict[str, BusinessRequirement] = {}
        for reqs in requirements_list:
            combined.update(reqs.root)  # Pydantic RootModel

        self.requirements_dict = combined
        self.threshold = threshold
        self.req_ids = list(self.requirements_dict.keys())

    @abstractmethod
    def classify(self, result: Result) -> list[str]:
        """
        Классифицирует результат и возвращает список подходящих BusinessRequirement ключей.
        """
        pass


class BayesianClassifier(Classifier):
    def __init__(self, requirements_list: list[BusinessRequirements], threshold: float = 0.3):
        super().__init__(requirements_list=requirements_list, threshold=threshold)

        texts = [
            f"{r.description} {r.useCase or ''} {' '.join(r.keywords)}"
            for r in self.requirements_dict.values()
        ]

        self.vectorizer = TfidfVectorizer()
        self.X = self.vectorizer.fit_transform(texts)

        # Простейший трюк: каждое требование — отдельный класс
        # Мы обучаем dummy классификацию: текст → req_id
        self.model = MultinomialNB()
        self.model.fit(self.X, self.req_ids)

    def classify(self, result: Result) -> list[str]:
        text = result.getPromptNode().getText()
        x_input = self.vectorizer.transform([text])
        probs = self.model.predict_proba(x_input)[0]

        matching = [
            req_id for req_id, p in zip(self.req_ids, probs, strict=False) if p >= self.threshold
        ]
        return matching

class TransformerClassifier(Classifier):
    def __init__(
        self,
        requirements_list: list[BusinessRequirements],
        model_name: str = "sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2",
        threshold: float = 0.1,
    ):
        super().__init__(requirements_list, threshold)

        self.model = SentenceTransformer(model_name)
        self.req_ids = list(self.requirements_dict.keys())
        self.req_texts = [
            f"{r.description} {r.useCase or ''} {' '.join(r.keywords)}"
            for r in self.requirements_dict.values()
        ]
        self.req_embeddings = self.model.encode(self.req_texts, convert_to_tensor=True, show_progress_bar=False)

    def classify(self, result: Result) -> list[str]:
        text = result.getPromptNode().getText()
        query_embedding = self.model.encode(text, convert_to_tensor=True, show_progress_bar=False)
        scores = util.cos_sim(query_embedding, self.req_embeddings)[0]

        matched = [
            req_id
            for req_id, score in zip(self.req_ids, scores, strict=False)
            if score >= self.threshold
        ]
        return matched