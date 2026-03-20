import os
import sys
from typing import List

import joblib
import numpy as np
import pandas as pd
from sklearn.neighbors import NearestNeighbors
from sklearn.preprocessing import MinMaxScaler
from umap import UMAP

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from domain.models.point import Point
from marker.marker import Marker
from services.scatter import Scatter
from services.vectorizer.pattern_vector import PatternVector
from services.vectorizer.vectorizer import Vectorizer


def prepare_data(
    input_file: str, output_file: str, offset: int = 10, limit: int = 1
) -> pd.DataFrame:

    df = pd.read_csv(input_file)
    df.columns = df.columns.str.lower()

    offset_rows = 12 * 24 * offset
    limit_rows = 12 * 24 * limit

    # Выбираем данные начиная с offset и берем limit строк
    df_period = df.iloc[offset_rows : offset_rows + limit_rows]
    df_period.to_csv(output_file, index=False)

    print(f"Сохранено {len(df_period)} строк в {output_file}")

    return df_period


def get_pattern_vectors(df: pd.DataFrame) -> List[PatternVector]:
    """
    Преобразует DataFrame в список PatternVector, каждый из которых
    содержит векторное представление паттерна и его направление.
    """
    marker = Marker(a_len=8)
    vectorizer = Vectorizer(feature_columns=["open", "high", "low", "close"])

    segments = marker.mark(df)

    # Обновляем характеристики паттерна для каждого сегмента
    for segment in segments:
        segment.update_pattern_characteristics()

    # Векторизуем сегменты
    vectors = []
    for segment in segments:
        vector = vectorizer.vectorize_pattern(segment, normalize=True)
        vectors.append(vector[0])

    return [
        PatternVector(vector=vec, direction=segment.get_direction())
        for vec, segment in zip(vectors, segments)
    ]


def fit_umap_model(pattern_vectors: List[PatternVector]) -> UMAP:
    vectors = np.array([pv.vector for pv in pattern_vectors])

    reducer = UMAP(
        n_components=2,
        n_neighbors=15,
        min_dist=0.05,
        metric="euclidean",
        random_state=42,
    )
    reducer.fit(vectors)
    return reducer


def transform_vectors(vectors: np.ndarray, reducer: UMAP) -> np.ndarray:
    """
    Transforms vectors using UMAP and scales them to [-1, 1] range.

    Args:
        vectors: Array of vectors to transform
        reducer: UMAP model for dimensionality reduction

    Returns:
        Array of shape (n_samples, 2) with transformed coordinates
    """
    transformed = reducer.transform(vectors)
    return MinMaxScaler(feature_range=(-1, 1)).fit_transform(transformed)  # type: ignore


def calculate_scan_radius_knn(
    coordinates: np.ndarray, target_neighbors: int = 4
) -> float:
    """
    Вычисляет scan_radius как медиану расстояний до k-го ближайшего соседа.

    Args:
        coordinates: массив координат точек [[x1, y1], [x2, y2], ...]
        target_neighbors: желаемое количество соседей

    Returns:
        Оптимальный scan_radius
    """
    if len(coordinates) < target_neighbors + 1:
        return 0.1

    # Находим k ближайших соседей для каждой точки
    k = min(
        target_neighbors + 1, len(coordinates)
    )  # +1 потому что точка сама себе сосед
    nbrs = NearestNeighbors(n_neighbors=k, algorithm="ball_tree").fit(coordinates)
    distances, indices = nbrs.kneighbors(coordinates)

    # Берем расстояния до k-го соседа (исключая саму точку)
    kth_distances = distances[:, -1]  # Последний элемент - самый дальний из k соседей

    # Возвращаем медиану этих расстояний с небольшим запасом
    return float(np.median(kth_distances) * 1.2)


def new_scatter_from_vectors(
    reducer: UMAP,
    pattern_vectors: List[PatternVector],
    min_group_size: int = 3,
) -> Scatter:
    """
    Creates Scatter object from pattern vectors.

    Args:
        reducer: UMAP model for dimensionality reduction
        pattern_vectors: list of PatternVector objects
        min_group_size: minimum size of point group
    """
    vectors = np.array([pv.vector for pv in pattern_vectors])
    transformed = transform_vectors(vectors, reducer)

    # Вычисляем scan_radius k-NN алгоритмом
    scan_radius = calculate_scan_radius_knn(transformed, target_neighbors=4)
    point_id = 0

    scatter = Scatter(
        min_group_size=min_group_size,
        sector_size=6.0,
        scan_radius=scan_radius,
    )

    for (x, y), pattern_vec in zip(transformed, pattern_vectors):
        point = Point(
            x=x,
            y=y,
            direction=pattern_vec.to_scatter_direction(),
            id=point_id,
            group_id=-1,
        )
        scatter.add_point(point)
        point_id += 1

    return scatter


def load_reducer(models_dir: str) -> UMAP:
    """Load UMAP reducer model from file."""

    reducer_path = os.path.join(models_dir, "umap_reducer.joblib")

    return joblib.load(reducer_path)


def save_reducer(reducer: UMAP, models_dir: str):
    """Save UMAP reducer model to file."""

    os.makedirs(models_dir, exist_ok=True)
    reducer_path = os.path.join(models_dir, "umap_reducer.joblib")
    joblib.dump(reducer, reducer_path)

    print(f"UMAP reducer saved to {reducer_path}")


def add_vectors(
    scatter: Scatter,
    pattern_vectors: List[PatternVector],
    reducer: UMAP,
) -> None:
    """
    Adds new pattern vectors to existing scatter plot.

    Args:
        scatter: Existing Scatter object
        pattern_vectors: List of PatternVector objects to add
        reducer: UMAP model for dimensionality reduction
    """
    vectors = np.array([pv.vector for pv in pattern_vectors])
    transformed = transform_vectors(vectors, reducer)

    last_id = scatter.get_last_id()

    for (x, y), pattern_vec in zip(transformed, pattern_vectors):
        point = Point(
            x=x,
            y=y,
            direction=pattern_vec.to_scatter_direction(),
            id=last_id,
            group_id=-1,
        )
        scatter.add_point(point)
        scatter.regroup(point)
        last_id += 1


def main():
    # === Этап 0: Определяем интересующие интервалы ===
    base_offset = 0  # период пропуска в сутках
    base_limit = 2  # первоначальный период в сутках
    new_period = 1  # новый период в сутках

    # === Этап 1: Обучаем UMAP на базовом периоде ===
    base_df = prepare_data(
        input_file="data/candles/BTCUSDT/raw/BTCUSDT_5m_klines.csv",
        output_file="data/candles/BTCUSDT/test/BTCUSDT_5m_base.csv",
        offset=0,
        limit=base_limit,
    )
    base_pattern_vectors = get_pattern_vectors(base_df)
    reducer = fit_umap_model(base_pattern_vectors)

    # === Этап 2: Сохраняем UMAP reducer
    models_dir = "data/models/BTCUSDT"
    save_reducer(reducer, models_dir)

    scatter = new_scatter_from_vectors(reducer, base_pattern_vectors)

    # === Этап 6: Группировка и визуализация ===
    scatter.scan_all_points()
    scatter.group()
    scatter.visualize("data/scatter/BTCUSDT/scatter_base_plot.png")
    print("Визуализация сохранена в scatter_base_plot.png")

    # === Этап 3: Получаем новые эпизоды, добавляем к базовым ===
    new_df = prepare_data(
        input_file="data/candles/BTCUSDT/raw/BTCUSDT_5m_klines.csv",
        output_file="data/candles/BTCUSDT/test/BTCUSDT_5m_latest.csv",
        offset=base_limit,
        limit=new_period,
    )
    new_pattern_vectors = get_pattern_vectors(new_df)

    add_vectors(scatter, new_pattern_vectors, reducer)

    # === Этап 6: Группировка и визуализация ===
    scatter.visualize("data/scatter/BTCUSDT/scatter_updated_plot.png")
    print("Визуализация сохранена в scatter_updated_plot.png")


if __name__ == "__main__":
    main()
