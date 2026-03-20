import copy
import math
import os
import sys
from collections import deque
from typing import List

import numpy as np
import pandas as pd
from scipy.spatial.distance import pdist
from sklearn.neighbors import NearestNeighbors
from sklearn.preprocessing import MinMaxScaler, StandardScaler
from umap import UMAP

# Add parent directory to path for imports
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from domain.models.point import Point
from domain.types.candle import Candle
from domain.types.direction import Direction
from marker.marker import Marker
from services.scatter import Scatter
from services.trade_engine import TradeEngineReversalV2
from services.vectorization.simple_vectorizer import get_pattern_vectors_with_ma
from services.vectorizer.pattern_vector import PatternVector
from services.vectorizer.vectorizer import Vectorizer
from utils.candle_utils import calculate_avg_candle_length


def prepare_test_data(input_file: str, offset: int = 0, limit: int = 1) -> pd.DataFrame:
    """Подготавливает тестовые данные за указанный период."""
    df = pd.read_csv(input_file)
    df.columns = df.columns.str.lower()

    offset_rows = 12 * 24 * offset
    limit_rows = 12 * 24 * limit

    return df.iloc[offset_rows : offset_rows + limit_rows]


def get_pattern_vectors(df: pd.DataFrame) -> List[PatternVector]:
    """
    Преобразует DataFrame в список PatternVector с новой 44-параметрической системой.
    Использует чистую архитектуру без смешивания ответственности.

    Args:
        df: DataFrame с данными свечей и MA колонками

    Returns:
        List[PatternVector] с векторами по 44 параметра
    """
    # Проверяем наличие необходимых колонок
    required_columns = ["open", "high", "low", "close", "volume"]
    missing_columns = [col for col in required_columns if col not in df.columns]

    if missing_columns:
        raise ValueError(f"Отсутствуют необходимые колонки: {missing_columns}")

    # Используем новую систему векторизации
    return get_pattern_vectors_with_ma(df)


def fit_umap_model(reducer: UMAP, pattern_vectors: List[PatternVector]) -> UMAP:
    """Обучает UMAP модель на нормализованных векторах паттернов."""
    import warnings

    # Векторы уже нормализованы в get_pattern_vectors(
    vectors = np.vstack([pv.vector for pv in pattern_vectors])

    # Подавляем известные предупреждения UMAP
    with warnings.catch_warnings():
        warnings.filterwarnings(
            "ignore",
            category=RuntimeWarning,
            message="divide by zero encountered in power",
        )
        warnings.filterwarnings(
            "ignore", category=UserWarning, message=".*n_jobs value.*overridden.*"
        )
        reducer.fit(vectors)

    return reducer


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


def create_base_scatter(
    reducer: UMAP,
    pattern_vectors: List[PatternVector],
    min_group_size: int = 3,
) -> Scatter:
    """
    Создает базовый scatter с обученными скейлерами.
    Этот scatter будет использоваться как основа для обоих тестов.

    Args:
        reducer: Обученная UMAP модель
        pattern_vectors: Нормализованные векторы для создания точек
        raw_pattern_vectors: Сырые векторы для обучения feature_scaler
    """
    # Векторы уже нормализованы в get_pattern_vectors(
    vectors = np.vstack([pv.vector for pv in pattern_vectors])
    transformed = reducer.transform(vectors)
    coords_scaler = MinMaxScaler(feature_range=(-1, 1))
    limited_coordinates = coords_scaler.fit_transform(transformed)  # type: ignore

    # Вычисляем scan_radius новым k-NN алгоритмом
    scan_radius = calculate_scan_radius_knn(limited_coordinates, target_neighbors=4)

    # Создаем scatter с нормализованными векторами
    scatter = Scatter.create_with_initial_data(
        training_vectors=vectors,
        reducer=reducer,
        min_group_size=min_group_size,
        sector_size=6.0,
    )
    # Устанавливаем правильный scan_radius
    scatter.scan_radius = scan_radius

    # Добавляем базовые точки
    for pattern_vec in pattern_vectors:
        vectors = pattern_vec.vector.reshape(1, -1)  # Преобразуем 1D в 2D для sklearn
        scaled_vectors = scatter.feature_scaler.transform(vectors)

        # Подавляем предупреждения UMAP
        import warnings

        with warnings.catch_warnings():
            warnings.filterwarnings(
                "ignore",
                category=RuntimeWarning,
                message="divide by zero encountered in power",
            )
            transformed = reducer.transform(scaled_vectors)

        coords = scatter.coords_scaler.transform(transformed)  # type: ignore

        point = Point(
            x=coords[0][0],
            y=coords[0][1],
            direction=pattern_vec.to_scatter_direction(),
            id=len(scatter.points),
            group_id=-1,
        )
        scatter.add_point(point)

    scatter.scan_all_points()
    scatter.group()

    return scatter


def to_candles(df: pd.DataFrame) -> List[Candle]:
    """Конвертирует DataFrame в список Candle."""
    candles = []
    for _, row in df.iterrows():
        candle = Candle(
            open=row["open"],
            high=row["high"],
            low=row["low"],
            close=row["close"],
            volume=row["volume"] if "volume" in row else 0,
        )
        candles.append(candle)
    return candles


if __name__ == "__main__":
    # === Prepare base data ===
    input_file = "data/candles/BTCUSDT/ma_added/BTCUSDT_5m_ma.csv"
    base_period = 2
    # === Prepare base scatter ===
    base_df = prepare_test_data(input_file, offset=0, limit=base_period)
    avg_candle = calculate_avg_candle_length(df=base_df)
    base_pattern_vectors = get_pattern_vectors(base_df)
    reducer = UMAP(
        n_components=2,
        n_neighbors=10,
        min_dist=2,
        spread=5,
        metric="euclidean",
        random_state=42,
    )
    reducer = fit_umap_model(reducer, base_pattern_vectors)
    scatter = create_base_scatter(
        reducer=reducer,
        pattern_vectors=base_pattern_vectors,
        min_group_size=3,
    )
    scatter.visualize("data/trade_engine/script_output/base_scatter.png")
    # === Prepare new candles data ===
    new_candles_df = prepare_test_data(input_file, offset=base_period, limit=1)
    new_candles = to_candles(new_candles_df)
    # === Prepare trade_engine ===
    # trade_engine = TradeEngineReversalV2(
    #    window=deque(maxlen=11),
    #    vectorizer=Vectorizer(),
    #    scatter=scatter,
    #    reducer=reducer,
    #    avg_candle_len=avg_candle,
    # )
    # for new_candle in new_candles:
    #    trade_engine.place(new_candle)
    # trade_engine.scatter.visualize(
    #    "data/trade_engine/script_output/TE_scatter.png"
    # )
    # trade_engine.scatter.visualize(
    #    "data/trade_engine/script_output/TE_scatter.png"
    # )
    # )
