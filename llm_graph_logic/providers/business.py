import json
from typing import Any

from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.naive_bayes import MultinomialNB

from llm_graph_logic.internal.enum import EdgeType, InfoType, NodeType
from llm_graph_logic.internal.graph import Edge, Graph, Node
from llm_graph_logic.internal.info_provider import InfoProvider


def _node_to_text(data: Any) -> str:
    """
    Рекурсивно преобразует данные узла в плоский текст.
    """
    if isinstance(data, str):
        return data
    if isinstance(data, (int, float, bool)):
        return str(data)
    if isinstance(data, list):
        return " ".join(_node_to_text(item) for item in data)
    if isinstance(data, dict):
        return " ".join(_node_to_text(v) for v in data.values())
    return ""

class BusinessInfoProvider(InfoProvider):
    """
    Провайдер, обогащающий граф бизнес-требованиями.
    Поддерживает мультиязычную классификацию через отдельные TF-IDF + Naive Bayes модели для каждого языка.
    Требования в JSON допускают поле 'language', например 'en' или 'ru'.
    """
    def __init__(self, requirements_file: str):
        super().__init__(InfoType.BUSINESS_PROVIDER)
        self.requirements_file = requirements_file
        self.requirements = self._load_requirements()
        # Группируем требования по языку
        self.lang_requirements: dict[str, list[tuple[str, dict[str, Any]]]] = {}
        for req_id, info in self.requirements.items():
            lang = info.get('language', 'default')
            self.lang_requirements.setdefault(lang, []).append((req_id, info))
        # Для каждой группы создаём векторизатор и классификатор
        self.vectorizers: dict[str, TfidfVectorizer] = {}
        self.classifiers: dict[str, MultinomialNB] = {}
        for lang, reqs in self.lang_requirements.items():
            texts, labels = [], []
            for req_id, info in reqs:
                desc = info.get('description', '')
                keywords = ' '.join(info.get('keywords', []))
                texts.append(f"{desc} {keywords}")
                labels.append(req_id)
            vect = TfidfVectorizer()
            clf = MultinomialNB()
            tfidf = vect.fit_transform(texts)
            clf.fit(tfidf, labels)
            self.vectorizers[lang] = vect
            self.classifiers[lang] = clf

    def _load_requirements(self) -> dict[str, dict[str, Any]]:
        with open(self.requirements_file, encoding='utf-8') as f:
            return json.load(f)

    def _detect_language(self, text: str) -> str:
        try:
            from langdetect import detect
            lang = detect(text)
        except Exception:
            lang = 'default'
        return lang if lang in self.classifiers else 'default'

    def _classify_node(self, node: Node, top_k: int = 2, threshold: float = 0.1) -> list[str]:
        # Преобразуем узел в текст
        text = _node_to_text(node.getData())
        # Определяем язык и выбираем модель
        lang = self._detect_language(text)
        vect = self.vectorizers.get(lang)
        clf = self.classifiers.get(lang)
        if not vect or not clf:
            return []
        vec = vect.transform([text])
        probs = clf.predict_proba(vec)[0]
        classes = clf.classes_
        ranked = sorted(zip(classes, probs, strict=False), key=lambda x: x[1], reverse=True)
        return [req for req, p in ranked if p >= threshold][:top_k]

    async def mutateGraph(self, graph: "Graph") -> "Graph":
        for node_id, node in list(graph.nodes.items()):
            if node.getType() != NodeType.ATTRIBUTE:
                continue
            matched_reqs = self._classify_node(node)
            if node.getType() not in [NodeType.ATTRIBUTE, NodeType.BLOCK]:
                continue
            for req_id in matched_reqs:
                req_info = self.requirements[req_id]
                info_id = f"info_business.{req_id}"
                if info_id not in graph.nodes:
                    info_node = Node(
                        info_id,
                        NodeType.BUSINESS_REQUIREMENT,
                        'business_info',
                        req_info
                    )
                    graph = graph.addNode(info_node)
                else:
                    info_node = graph.nodes[info_id]
                graph = graph.addEdge(Edge(info_node, node, EdgeType.INFO))
                if node.getType() == NodeType.ATTRIBUTE: # Через description или аттрибуты прокидываем информацию в блок
                    nearestBlockNodes = [edge.to for _, edge in graph.edges.get(node.getID(), {}).items()]
                    for blockNode in nearestBlockNodes:
                        graph = graph.addEdge(Edge(info_node, blockNode, EdgeType.INFO))
        return graph