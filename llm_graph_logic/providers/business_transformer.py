
import json
from pathlib import Path
from typing import Any, List, Optional

import numpy as np
from pydantic import BaseModel, Field, RootModel
import torch
from sentence_transformers import SentenceTransformer, util

from llm_graph_logic.internal.enum import EdgeType, InfoType, NodeType
from llm_graph_logic.internal.graph import Edge, Graph, Node
from llm_graph_logic.internal.info_provider import InfoProvider


class BusinessRequirement(BaseModel):
    """
    Структура описания одного бизнес-требования
    """
    description: str = Field(..., description="Текстовое описание требования")
    keywords: List[str] = Field(..., description="Ключевые слова, связанные с требованием")
    language: str = Field(..., description="Язык требования, например: 'en', 'ru'")
    useCase: Optional[str] = Field(..., description="Пример использования или мотивирующий кейс")


class BusinessRequirements(RootModel[dict[str, BusinessRequirement]]):
    """
    Полная коллекция требований, индексированная по уникальному req_id (например, 'REQ_01')
    """
    pass

def _node_to_text(data: Any) -> str:
    """
    Рекурсивно преобразует данные узла в плоский текст,
    объединяя ключи и значения, чтобы модель лучше «понимала» контекст.
    """
    if isinstance(data, str):
        return data
    if isinstance(data, int | float | bool):
        return str(data)
    if isinstance(data, list):
        return " ".join(_node_to_text(item) for item in data)
    if isinstance(data, dict):
        parts: list[str] = []
        for key, value in data.items():
            # Добавляем название поля вместе со значением
            parts.append(str(key))
            parts.append(_node_to_text(value))
        return " ".join(parts)
    return ""

class TransformerBusinessInfoProvider(InfoProvider):
    """
    Провайдер, обогащающий граф бизнес-требованиями, используя sentence-transformers.
    Использует Pydantic-схему BusinessRequirements для загрузки требований.
    """

    def __init__(
        self,
        requirements_file_path: Path,
        model_name: str = "sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2",
    ):
        super().__init__(InfoType.BUSINESS_PROVIDER)
        self.requirements_file_path = requirements_file_path

        # Загружаем и валидируем требования
        self.requirements_model: BusinessRequirements = self._load_requirements()
        self.requirements: dict[str, BusinessRequirement] = self.requirements_model.root

        # Настраиваем модель
        self.device = "cuda" if torch.cuda.is_available() else "cpu"
        self.model = SentenceTransformer(model_name, device=self.device)

        # Готовим данные к кодированию
        self.req_ids: list[str] = []
        self.req_infos: list[BusinessRequirement] = []
        texts_to_encode: list[str] = []

        for req_id, info in self.requirements.items():
            combined = f"{info.description} {info.useCase or ''} {' '.join(info.keywords)}".strip()
            texts_to_encode.append(combined)
            self.req_ids.append(req_id)
            self.req_infos.append(info)

        # Эмбеддинги
        if texts_to_encode:
            self.req_embeddings = self.model.encode(
                texts_to_encode, convert_to_tensor=True, show_progress_bar=False
            )
        else:
            self.req_embeddings = torch.zeros(
                (0, self.model.get_sentence_embedding_dimension()),
                device=self.device,
            )

    def getRequirementsModel(self) -> BusinessRequirements:
        return self.requirements_model

    def _load_requirements(self) -> BusinessRequirements:
        with self.requirements_file_path.open("r", encoding="utf-8") as f:
            data = json.load(f)
            return BusinessRequirements.model_validate(data)

    @torch.no_grad()
    def _classify_node(
        self,
        node: Node,
        top_k: int = 2,
        threshold: float = 0.3,
    ) -> list[tuple[str, float]]:
        data = node.getData()
        text = _node_to_text(data)

        if not text.strip() or len(self.req_ids) == 0:
            return []

        emb_node = self.model.encode(text, convert_to_tensor=True, show_progress_bar=False)
        cos_scores = util.cos_sim(emb_node, self.req_embeddings)[0].cpu().numpy()

        ranked_idx = np.argsort(-cos_scores)
        results: list[tuple[str, float]] = []

        for idx in ranked_idx[:top_k]:
            score = float(cos_scores[idx])
            if score >= threshold:
                results.append((self.req_ids[idx], score))

        return results

    async def mutateGraph(self, graph: "Graph") -> "Graph":
        for _, node in list(graph.nodes.items()):
            if node.getType() not in (NodeType.ATTRIBUTE, NodeType.BLOCK):
                continue

            matched = self._classify_node(node, top_k=3, threshold=0.25)
            if not matched:
                continue

            for req_id, score in matched:
                req_info = self.requirements[req_id]
                info_id = f"info_business.{req_id}"

                if info_id not in graph.nodes:
                    info_node = Node(
                        info_id,
                        NodeType.BUSINESS_REQUIREMENT,
                        "business_info",
                        req_info.dict(),
                    )
                    graph = graph.addNode(info_node)
                else:
                    info_node = graph.nodes[info_id]

                if node.getType() == NodeType.ATTRIBUTE:
                    parent_edges = graph.edges.get(node.getID(), {}).values()
                    for edge in parent_edges:
                        if edge.getType() == EdgeType.ATTRIBUTE_BLOCK:
                            parent_node = edge.to
                            graph = graph.addEdge(Edge(info_node, parent_node, EdgeType.INFO))
                else:
                    graph = graph.addEdge(Edge(info_node, node, EdgeType.INFO))

        return graph
