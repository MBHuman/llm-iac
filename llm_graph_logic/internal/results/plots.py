from pathlib import Path
from typing import Any

import matplotlib.pyplot as plt


class PlotsProcessor:
    """
    PlotsProcessor отвечает за отрисовку графиков, полученных из ResultPlots.
    Поддерживает как линейные графики, так и barplot.
    """

    def process(self, result_plots: "ResultPlots") -> None:
        for plot_config in result_plots._plots_data:
            x = plot_config["x"]
            y = plot_config["y"]
            label = plot_config.get("label", None)
            kind = plot_config.get("kind", "line")

            plt.figure()
            if kind == "bar":
                plt.bar(x, y, label=label)
            else:
                plt.plot(x, y, label=label)

            if result_plots.title:
                plt.title(result_plots.title)
            if result_plots.xlabel:
                plt.xlabel(result_plots.xlabel)
            if result_plots.ylabel:
                plt.ylabel(result_plots.ylabel)
            if label:
                plt.legend()
            plt.show()


class ResultPlots:
    """
    Класс-«продукт» паттерна Builder, содержащий данные для графиков
    и методы для их отображения через PlotsProcessor и сохранения в файлы.
    """

    def __init__(
        self,
        plots_data: list[dict[str, Any]],
        title: str | None = None,
        xlabel: str | None = None,
        ylabel: str | None = None,
        useTitleForSaveName: bool = False,
    ) -> None:
        self._plots_data = plots_data
        self.title = title
        self.xlabel = xlabel
        self.ylabel = ylabel
        self.useTitleForSaveName = useTitleForSaveName

    def draw(self) -> None:
        processor = PlotsProcessor()
        processor.process(self)

    def save(self, path: Path) -> None:
        if not path.exists():
            path.mkdir(parents=True, exist_ok=True)

        for idx, plot_config in enumerate(self._plots_data):
            x = plot_config["x"]
            y = plot_config["y"]
            label = plot_config.get("label", None)
            kind = plot_config.get("kind", "line")

            fig = plt.figure()
            if kind == "bar":
                plt.bar(x, y, label=label)
            else:
                plt.plot(x, y, label=label)

            if self.title:
                plt.title(self.title)
            if self.xlabel:
                plt.xlabel(self.xlabel)
            if self.ylabel:
                plt.ylabel(self.ylabel)
            if label:
                plt.legend()

            filename = path / f"plot_{idx}.png"
            if self.useTitleForSaveName and label:
                filename = path / f"plot_{label}.png"
            fig.savefig(str(filename))
            plt.close(fig)


class ResultPlotsBuilder:
    """
    Builder для постепенного добавления данных и метаданных графиков.
    """

    def __init__(self) -> None:
        self._plots_data: list[dict[str, Any]] = []
        self._title: str | None = None
        self._xlabel: str | None = None
        self._ylabel: str | None = None
        self.useTitleForName: bool = False

    def set_title(self, title: str) -> "ResultPlotsBuilder":
        self._title = title
        return self

    def set_xlabel(self, xlabel: str) -> "ResultPlotsBuilder":
        self._xlabel = xlabel
        return self

    def set_ylabel(self, ylabel: str) -> "ResultPlotsBuilder":
        self._ylabel = ylabel
        return self

    def setUseTitleForName(self) -> "ResultPlotsBuilder":
        self.useTitleForName = True
        return self

    def add_plot(
        self,
        x: list[Any],
        y: list[Any],
        label: str | None = None,
        kind: str = "line",
    ) -> "ResultPlotsBuilder":
        self._plots_data.append({"x": x, "y": y, "label": label, "kind": kind})
        return self

    def build(self) -> ResultPlots:
        return ResultPlots(
            plots_data=self._plots_data,
            title=self._title,
            xlabel=self._xlabel,
            ylabel=self._ylabel,
            useTitleForSaveName=self.useTitleForName,
        )
