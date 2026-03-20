from dataclasses.segment import Direction, Segment
from typing import Dict, List, Tuple

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from sklearn.decomposition import PCA
from sklearn.manifold import TSNE
from sklearn.preprocessing import MinMaxScaler, RobustScaler, StandardScaler
from vectorizer.vectorizer import Vectorizer

from marker.marker import Marker
from marker.pattern_analyzer import PatternAnalyzer


def create_feature_combinations():
    """
    Создает комбинации характеристик для анализа.
    """
    features = [
        ["open", "high", "low", "close"],
        ["open", "high", "low", "close", "volume"],
    ]
    return features


def apply_feature_combination(vectors: np.ndarray, combo: Dict) -> np.ndarray:
    """
    Применяет комбинацию параметров к векторам
    """
    # Применяем веса к соответствующим компонентам вектора
    weighted_vectors = vectors.copy()
    feature_indices = {
        "rel_volatility": 0,
        "rel_price_range": 1,
        "body_sizes": 2,
        "shadows": (3, 4),  # upper and lower shadows
        "volume": (5, 6),  # volume and volume trend
        "momentum": (7, 8),  # momentum strength and uniformity
        "patterns": (9, 10, 11),  # doji, hammer, engulfing
        "trend": (12, 13),  # trend strength and angle
        "gaps": (14, 15),  # gaps and overlaps
    }

    for feature, weight in combo["weights"].items():
        if feature in combo["features"]:
            idx = feature_indices[feature]
            if isinstance(idx, tuple):
                weighted_vectors[:, idx[0] : idx[-1] + 1] *= weight
            else:
                weighted_vectors[:, idx] *= weight

    # Применяем нормализацию
    return combo["scaler"].fit_transform(weighted_vectors)


def plot_pattern_vectors(vectors, directions, title, description, ax):
    """
    Отображает векторы паттернов с использованием t-SNE.

    Args:
        vectors: массив векторов паттернов
        directions: список направлений движения после паттернов
        title: заголовок графика
        description: описание для графика
        ax: объект осей для отрисовки
    """
    # Преобразуем векторы с помощью t-SNE
    tsne = TSNE(
        n_components=2,
        perplexity=30,
        max_iter=1000,
        random_state=42,
    )
    transformed = tsne.fit_transform(vectors)

    # Создаем анализатор паттернов
    analyzer = PatternAnalyzer(dominance_threshold=0.75, n_neighbors=10, grid_size=20)
    analyzer.fit(transformed, directions)

    # Получаем вероятности для каждой точки
    probabilities = analyzer.predict_proba(transformed)

    # Разделяем точки по направлениям
    up_mask = np.array(directions) == 1
    down_mask = ~up_mask

    # Создаем цветовую карту
    colors = np.where(up_mask, "red", "blue")

    # Получаем сетку вероятностей для контуров
    xx, yy, zz = analyzer.get_grid_probabilities(transformed)

    # Отображаем точки
    if "Dominant Areas" in title:
        # Для центрального графика показываем все точки и контуры
        ax.scatter(transformed[:, 0], transformed[:, 1], c=colors, alpha=0.5, s=10)

        # Добавляем контурные линии для областей UP (вероятности 0.75-0.95)
        levels_up = [0.75, 0.85, 0.95]
        contour_up = ax.contour(
            xx, yy, zz[:, :, 1], levels=levels_up, colors=["red"], alpha=0.3
        )

        # Добавляем контурные линии для областей DOWN (вероятности 0.05-0.25)
        levels_down = [0.05, 0.15, 0.25]
        contour_down = ax.contour(
            xx, yy, zz[:, :, 1], levels=levels_down, colors=["blue"], alpha=0.3
        )

    elif "Inside Contours" in title:
        # Создаем маску для точек внутри контуров
        up_contour_mask = probabilities[:, 1] >= 0.75  # Вероятность UP >= 75%
        down_contour_mask = probabilities[:, 1] <= 0.25  # Вероятность DOWN >= 75%
        contour_mask = up_contour_mask | down_contour_mask

        # Фильтруем точки и цвета
        filtered_points = transformed[contour_mask]
        filtered_colors = colors[contour_mask]

        # Показываем только отфильтрованные точки
        ax.scatter(
            filtered_points[:, 0],
            filtered_points[:, 1],
            c=filtered_colors,
            alpha=0.5,
            s=10,
        )

        # Добавляем контурные линии для областей UP (вероятности 0.75-0.95)
        levels_up = [0.75, 0.85, 0.95]
        contour_up = ax.contour(
            xx, yy, zz[:, :, 1], levels=levels_up, colors=["red"], alpha=0.3
        )

        # Добавляем контурные линии для областей DOWN (вероятности 0.05-0.25)
        levels_down = [0.05, 0.15, 0.25]
        contour_down = ax.contour(
            xx, yy, zz[:, :, 1], levels=levels_down, colors=["blue"], alpha=0.3
        )

        # Добавляем информацию о количестве отфильтрованных точек
        total_points = len(transformed)
        filtered_points_count = len(filtered_points)
        up_points = np.sum(filtered_colors == "red")
        down_points = np.sum(filtered_colors == "blue")
        percentage = (filtered_points_count / total_points) * 100

        info_text = (
            f"Points in contours: {filtered_points_count} ({percentage:.1f}%)\n"
            f"UP points: {up_points}\n"
            f"DOWN points: {down_points}"
        )
        ax.text(
            0.02,
            0.98,
            info_text,
            transform=ax.transAxes,
            verticalalignment="top",
            fontsize=8,
        )
    else:
        # Для левого графика показываем все точки
        ax.scatter(transformed[:, 0], transformed[:, 1], c=colors, alpha=0.5, s=10)

    ax.set_title(title)
    ax.text(0.02, 0.02, description, transform=ax.transAxes)


def get_pattern_vectors(df, features, a_len):
    """
    Получает векторы паттернов и их направления для заданной длины прелюдии и набора характеристик.

    Args:
        df: DataFrame с данными
        features: список характеристик для векторизации
        a_len: длина прелюдии

    Returns:
        vectors: массив векторов паттернов
        directions: список направлений движения после паттернов
    """
    # Создаем маркер с текущей длиной прелюдии
    marker = Marker(a_len=a_len)

    # Маркируем сегменты
    segments = marker.mark(df)

    # Создаем векторайзер с текущими параметрами
    vectorizer = Vectorizer(feature_columns=features)

    # Обновляем характеристики паттерна для каждого сегмента
    for segment in segments:
        segment.update_pattern_characteristics()

    # Векторизуем паттерны
    vectors = []
    for segment in segments:
        vector = vectorizer.vectorize_pattern(segment, normalize=True)
        vectors.append(vector[0])

    # Получаем направления
    directions = [segment.get_direction() for segment in segments]

    return vectors, directions


def main():
    # Загружаем данные за год (5-минутный таймфрейм)
    df = pd.read_csv("data/candles/BTCUSDT/raw/BTCUSDT_5m_klines.csv")

    # Приводим названия столбцов к нижнему регистру
    df.columns = df.columns.str.lower().str.replace(" ", "_")

    total_rows = (
        12 * 24 * 30 * 12
    )  # примерно год (12 5-минуток в час * 24 часа * 30 дней * 12 месяцев)
    df = df.tail(total_rows)  # берем последний год

    # Разделяем на две части: для анализа паттернов и для тестирования
    train_df = df.head(total_rows // 2)  # первые 6 месяцев для анализа
    print(f"Размер данных для анализа паттернов: {len(train_df)} строк")

    # Получаем комбинации параметров
    feature_combinations = create_feature_combinations()

    # Определяем размеры сетки
    a_lens = [8]  # только 8 свечей

    # Создаем фигуру с тремя графиками
    fig, axes = plt.subplots(1, 3, figsize=(30, 10))

    # Получаем векторы и направления
    vectors, directions = get_pattern_vectors(
        train_df, feature_combinations[0], a_lens[0]
    )

    # Преобразуем векторы с помощью t-SNE (делаем один раз для всех графиков)
    tsne = TSNE(
        n_components=2,
        perplexity=30,
        max_iter=1000,
        random_state=42,
    )
    transformed = tsne.fit_transform(vectors)

    # Создаем анализатор паттернов (один для всех графиков)
    analyzer = PatternAnalyzer(dominance_threshold=0.75, n_neighbors=10, grid_size=20)
    analyzer.fit(transformed, directions)

    # График 1: Все точки
    scatter1 = axes[0].scatter(
        transformed[:, 0],
        transformed[:, 1],
        c=["red" if str(d) == "Direction.UP" else "blue" for d in directions],
        alpha=0.6,
        s=50,
    )
    axes[0].set_title("Все точки")
    axes[0].legend(["UP", "DOWN"])
    axes[0].grid(True, alpha=0.3)

    # График 2: Точки с контурами
    # Создаем сетку для контурного графика
    x_min, x_max = transformed[:, 0].min() - 1, transformed[:, 0].max() + 1
    y_min, y_max = transformed[:, 1].min() - 1, transformed[:, 1].max() + 1
    xx, yy = np.meshgrid(np.linspace(x_min, x_max, 100), np.linspace(y_min, y_max, 100))
    grid_points = np.c_[xx.ravel(), yy.ravel()]

    # Получаем вероятности для каждой точки сетки
    grid_probas = analyzer.predict_proba(grid_points)
    grid_probas = grid_probas.reshape(xx.shape)

    # Рисуем контуры для областей с преобладающим направлением UP (красный)
    levels_up = [0.75, 0.8, 0.85, 0.9, 0.95]
    cs_up = axes[1].contour(
        xx, yy, grid_probas, levels=levels_up, colors=["red"], alpha=0.8, linewidths=2
    )
    axes[1].clabel(cs_up, inline=True, fontsize=8, fmt="%.2f")

    # Рисуем контуры для областей с преобладающим направлением DOWN (синий)
    levels_down = [0.05, 0.1, 0.15, 0.2, 0.25]
    cs_down = axes[1].contour(
        xx,
        yy,
        grid_probas,
        levels=levels_down,
        colors=["blue"],
        alpha=0.8,
        linewidths=2,
    )
    axes[1].clabel(cs_down, inline=True, fontsize=8, fmt="%.2f")

    # Отображаем все точки на втором графике
    scatter2 = axes[1].scatter(
        transformed[:, 0],
        transformed[:, 1],
        c=["red" if str(d) == "Direction.UP" else "blue" for d in directions],
        alpha=0.6,
        s=50,
    )

    # Настраиваем второй график
    axes[1].set_title("Точки с контурами")
    axes[1].legend(["UP", "DOWN"])
    axes[1].grid(True, alpha=0.3)

    # График 3: Только точки в доминантных областях
    # Получаем вероятности для каждой точки
    point_probas = analyzer.predict_proba(transformed)

    # Создаем маску для точек внутри контуров
    inside_contours = (point_probas >= 0.75) | (point_probas <= 0.25)

    # Рисуем контуры для областей с преобладающим направлением UP (красный)
    cs_up = axes[2].contour(
        xx, yy, grid_probas, levels=levels_up, colors=["red"], alpha=0.8, linewidths=2
    )
    axes[2].clabel(cs_up, inline=True, fontsize=8, fmt="%.2f")

    # Рисуем контуры для областей с преобладающим направлением DOWN (синий)
    cs_down = axes[2].contour(
        xx,
        yy,
        grid_probas,
        levels=levels_down,
        colors=["blue"],
        alpha=0.8,
        linewidths=2,
    )
    axes[2].clabel(cs_down, inline=True, fontsize=8, fmt="%.2f")

    # Отображаем только точки внутри контуров
    filtered_points = transformed[inside_contours]
    filtered_directions = np.array(directions)[inside_contours]

    scatter3 = axes[2].scatter(
        filtered_points[:, 0],
        filtered_points[:, 1],
        c=["red" if str(d) == "Direction.UP" else "blue" for d in filtered_directions],
        alpha=0.6,
        s=50,
    )

    # Добавляем информацию о фильтрации
    filtered_count = np.sum(inside_contours)
    total_count = len(vectors)
    filter_info = f"Отфильтровано {filtered_count} из {total_count} точек"

    # Настраиваем график
    axes[2].set_title(f"Только точки в доминантных областях\n{filter_info}")
    axes[2].legend(["UP", "DOWN"])
    axes[2].grid(True, alpha=0.3)

    # Сохраняем визуализацию
    plt.tight_layout()
    plt.savefig("pattern_visualization.png", dpi=300, bbox_inches="tight")
    print("Визуализация сохранена в pattern_visualization.png")


if __name__ == "__main__":
    main()
