import csv
from dataclasses import dataclass
from pathlib import Path

import torch
from pydantic import BaseModel, Field
from sentence_transformers import SentenceTransformer, util
from sklearn.metrics import (
    accuracy_score,
    jaccard_score,
    precision_recall_fscore_support,
)
from sklearn.preprocessing import MultiLabelBinarizer


@dataclass
class Place:
    spanText: str
    requirementsKeys: list[str]


    def to_dict(self) -> dict:
        return {
            "requirementsKeys": self.requirementsKeys,
            "spanText": self.spanText,
        }


class Metrics(BaseModel):
    precision: float = Field(..., ge=0, le=1)
    recall: float = Field(..., ge=0, le=1)
    f1: float = Field(..., ge=0, le=1)
    jaccard: float = Field(..., ge=0, le=1)


class MultiAverageComparisonResult(BaseModel):
    gold: list[dict]
    predicted: list[dict]
    all_metrics: dict[str, Metrics]

    def save_to_csv(
        self,
        filepath: str | Path,
        category: str,
        model_name: str,
        project_name: str
    ) -> None:
        """
        Сохраняет метрики в CSV-файл.
        В начале файла добавляются строки-комментарии с информацией о модели и проекте.

        :param filepath: путь к выходному CSV-файлу
        :param model_name: название или идентификатор модели
        :param project_name: название проекта
        """
        # Убедимся, что директория для файла существует
        filepath = Path(filepath)
        filepath.parent.mkdir(parents=True, exist_ok=True)

        with filepath.open("w", newline="", encoding="utf-8") as csvfile:
            # Комментарии: начинаются с '#' — не будут парситься как данные
            csvfile.write(f"# Model: {model_name}\n")
            csvfile.write(f"# Project: {project_name}\n")
            csvfile.write(f"# Generated on: {Path.cwd() / filepath.name}\n\n")

            writer = csv.writer(csvfile)
            # Заголовок таблицы
            writer.writerow(["category", "project_name", "model_name", "metric", "precision", "recall", "f1", "jaccard"])

            # Записываем каждую метрику
            for metric_name, metrics in self.all_metrics.items():
                writer.writerow([
                    category,
                    project_name,
                    model_name,
                    metric_name,
                    f"{metrics.precision:.4f}",
                    f"{metrics.recall:.4f}",
                    f"{metrics.f1:.4f}",
                    f"{metrics.jaccard:.4f}",
                ])


class Comparator:
    def __init__(self, model_name: str = "sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2"):
        self.places: list[Place] = []

        self.device = "cuda" if torch.cuda.is_available() else "cpu"
        self.model = SentenceTransformer(model_name, device=self.device)
        self._place_embeddings: torch.Tensor | None = None

    def addPlace(self, place: Place) -> "Comparator":
        self.places.append(place)
        self._place_embeddings = None
        return self

    def _ensure_embeddings(self) -> None:
        if self._place_embeddings is not None:
            return
        texts = [p.spanText for p in self.places]
        if texts:
            self._place_embeddings = self.model.encode(texts, convert_to_tensor=True, show_progress_bar=False)
        else:
            self._place_embeddings = torch.zeros((0, self.model.get_sentence_embedding_dimension()), device=self.device)

    def searchPlace(self, searchText: str, threshold: float = 0.6) -> Place | None:
        self._ensure_embeddings()
        if self._place_embeddings is None or self._place_embeddings.shape[0] == 0:
            return None


        query_embedding = self.model.encode(searchText, convert_to_tensor=True, show_progress_bar=False)
        scores = util.cos_sim(query_embedding, self._place_embeddings)[0]
        best_score, best_idx = float(scores.max()), int(scores.argmax())

        if best_score >= threshold:
            return self.places[best_idx]
        return None

    def compare_places(self, gold_places: list[Place]) -> MultiAverageComparisonResult:
        gold_dicts, pred_dicts = [], []
        y_true: list[set[str]] = []
        y_pred: list[set[str]] = []

        for gold in gold_places:
            pred = self.searchPlace(gold.spanText) or Place(spanText=gold.spanText, requirementsKeys=[])

            gold_dicts.append(gold.to_dict())
            pred_dicts.append(pred.to_dict())

            y_true.append(set(gold.requirementsKeys))
            y_pred.append(set(pred.requirementsKeys))

        # Преобразуем в бинарную матрицу
        mlb = MultiLabelBinarizer()
        mlb.fit(y_true + y_pred)
        y_true_bin = mlb.transform(y_true)
        y_pred_bin = mlb.transform(y_pred)

        # Метрики
        precision_macro, recall_macro, f1_macro, _ = precision_recall_fscore_support(
            y_true_bin, y_pred_bin, average="macro", zero_division=0
        )
        precision_micro, recall_micro, f1_micro, _ = precision_recall_fscore_support(
            y_true_bin, y_pred_bin, average="micro", zero_division=0
        )
        precision_samples, recall_samples, f1_samples, _ = precision_recall_fscore_support(
            y_true_bin, y_pred_bin, average="samples", zero_division=0
        )

        jaccard_macro = jaccard_score(y_true_bin, y_pred_bin, average="macro", zero_division=1)
        jaccard_micro = jaccard_score(y_true_bin, y_pred_bin, average="micro", zero_division=1)
        jaccard_samples = jaccard_score(y_true_bin, y_pred_bin, average="samples", zero_division=1)

        subset_accuracy = accuracy_score(y_true_bin, y_pred_bin)

        metrics_result: dict[str, Metrics] = {
            "micro": Metrics(precision=precision_micro, recall=recall_micro, f1=f1_micro, jaccard=jaccard_micro),
            "macro": Metrics(precision=precision_macro, recall=recall_macro, f1=f1_macro, jaccard=jaccard_macro),
            "samples": Metrics(precision=precision_samples, recall=recall_samples, f1=f1_samples, jaccard=jaccard_samples),
            "subset": Metrics(precision=subset_accuracy, recall=subset_accuracy, f1=subset_accuracy, jaccard=subset_accuracy),
        }

        return MultiAverageComparisonResult(
            gold=gold_dicts,
            predicted=pred_dicts,
            all_metrics=metrics_result,
        )
