import glob
from pathlib import Path

import matplotlib.pyplot as plt

# Импортируем классы из вашего модуля
from llm_graph_logic.internal.results.plots import ResultPlotsBuilder


def test_builder_constructs_resultplots():
    """
    Проверяем, что ResultPlotsBuilder правильно накапливает данные и строит объект ResultPlots
    с ожидаемыми атрибутами.
    """
    builder = ResultPlotsBuilder()
    builder.set_title("Test Title") \
           .set_xlabel("X Axis") \
           .set_ylabel("Y Axis") \
           .add_plot([1, 2, 3], [4, 5, 6], label="Line 1")
    result_plots = builder.build()

    # Проверяем, что метаданные сохранились
    assert result_plots.title == "Test Title"
    assert result_plots.xlabel == "X Axis"
    assert result_plots.ylabel == "Y Axis"

    # Проверяем, что в _plots_data ровно один элемент с правильными полями
    assert isinstance(result_plots._plots_data, list)
    assert len(result_plots._plots_data) == 1
    plot_cfg = result_plots._plots_data[0]
    assert plot_cfg["x"] == [1, 2, 3]
    assert plot_cfg["y"] == [4, 5, 6]
    assert plot_cfg["label"] == "Line 1"


def test_save_creates_png_files(tmp_path, monkeypatch):
    """
    Проверяем, что ResultPlots.save() создает PNG-файлы в нужной директории.
    Фактическая папка для сохранений: tests/internal/results/plots
    """
    # Определим папку, куда должны сохраняться изображения
    base_dir = Path('tests/internal/results/plots')  # tests/internal/results/plots
    save_dir = base_dir / "output_test"
    # Убедимся, что поначалу папка отсутствует, чтобы проверить создание
    if save_dir.exists():
        for f in save_dir.iterdir():
            if f.suffix == ".png":
                f.unlink()
        save_dir.rmdir()

    # Создадим builder и два графика
    builder = ResultPlotsBuilder()
    builder.set_title("Save Test") \
           .set_xlabel("X") \
           .set_ylabel("Y") \
           .add_plot([0, 1, 2], [2, 4, 6], label="Line A", kind='bar') \
           .add_plot([0, 1, 2], [3, 6, 9], label="Line B")
    result_plots = builder.build()

    # Перекроем plt.show(), чтобы не пытался показать окно, но нам не нужно его вызывать при save()
    monkeypatch.setattr(plt, "show", lambda *args, **kwargs: None)

    # Вызываем save()
    result_plots.save(save_dir)

    # Проверяем, что директория создана
    assert save_dir.exists() and save_dir.is_dir()

    # Проверяем, что в ней ровно два файла plot_0.png и plot_1.png
    saved = sorted(glob.glob(str(save_dir / "plot_*.png")))
    assert len(saved) == 2

    # Проверяем существование конкретных имен файлов
    assert (save_dir / "plot_0.png").exists()
    assert (save_dir / "plot_1.png").exists()


def test_draw_calls_plotsprocessor(tmp_path, monkeypatch):
    """
    Проверяем, что метод draw() вызывает PlotsProcessor.process(),
    то есть при рисовании он использует plt.show() (мы подменим его и проверим, что он вызван).
    """
    # Создадим builder с одним графиком
    builder = ResultPlotsBuilder()
    builder.add_plot([0, 1], [1, 2], label="LineX")
    result_plots = builder.build()

    # Подменим plt.show, чтобы отлавливать вызовы
    called = {"count": 0}
    def fake_show(*args, **kwargs):
        called["count"] += 1
    monkeypatch.setattr(plt, "show", fake_show)

    # Вызов draw() должен привести к одному вызову fake_show()
    result_plots.draw()
    assert called["count"] == 1
