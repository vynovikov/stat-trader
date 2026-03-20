from typing import List, Optional

import numpy as np
import pandas as pd

from domain.models.segment import Segment
from marker.marker import Marker
from services.vectorizer.pattern_vector import PatternVector


def get_pattern_vectors_with_ma(df: pd.DataFrame) -> List[PatternVector]:
    """
    Извлекает векторы паттернов с MA данными используя чистую архитектуру.

    Args:
        df: DataFrame с ценовыми данными и MA колонками

    Returns:
        Список PatternVector с 44-параметрическими векторами
    """
    # Проверяем наличие необходимых колонок
    required_columns = ["open", "high", "low", "close", "volume"]
    ma_columns = ["ma_50", "ma_200"]

    missing_required = [col for col in required_columns if col not in df.columns]
    missing_ma = [col for col in ma_columns if col not in df.columns]

    if missing_required:
        raise ValueError(f"Missing required columns: {missing_required}")

    if missing_ma:
        print(f"Warning: Missing MA columns: {missing_ma}")

    # 1. Получаем сегменты от чистого маркера
    marker = Marker(a_len=8)
    segments = marker.mark(df)

    print(f"Found {len(segments)} segments from marker")

    # 2. Векторизуем сегменты с MA данными
    result = []

    for i, segment in enumerate(segments):
        if len(segment.Pre) == 8:  # Только полные прелюдии
            try:
                # Извлекаем MA данные для сегмента
                ma50_values = extract_ma_for_segment_simple(df, segment, "ma_50")
                ma200_values = extract_ma_for_segment_simple(df, segment, "ma_200")

                # Обновляем характеристики с MA данными
                segment.update_pattern_characteristics(ma50_values, ma200_values)

                # Получаем 44-параметрический вектор
                vector = segment.get_pattern_vector()

                # Создаем PatternVector
                pattern_vector = PatternVector(
                    vector=vector, direction=segment.get_direction()
                )
                result.append(pattern_vector)

            except Exception as e:
                print(f"Warning: Failed to vectorize segment {i} - {e}")
                continue

    print(f"Successfully vectorized {len(result)} segments")
    return result


def extract_ma_for_segment_simple(
    df: pd.DataFrame, segment: Segment, ma_column: str
) -> Optional[List[float]]:
    """
    Упрощенная версия извлечения MA данных для сегмента.
    Использует последовательный поиск по OHLC значениям.

    Args:
        df: DataFrame с данными
        segment: Сегмент для которого нужны MA данные
        ma_column: Название колонки с MA

    Returns:
        Список MA значений для 8 свечей или None
    """
    if ma_column not in df.columns:
        return None

    if len(segment.Pre) != 8:
        return None

    try:
        ma_values = []
        used_indices = set()  # Чтобы не использовать один индекс дважды

        for candle in segment.Pre:
            # Ищем точное совпадение OHLC значений
            matches = df[
                (df["open"] == candle.open)
                & (df["high"] == candle.high)
                & (df["low"] == candle.low)
                & (df["close"] == candle.close)
                & (df["volume"] == candle.volume)
            ]

            # Исключаем уже использованные индексы
            matches = matches[~matches.index.isin(used_indices)]

            if not matches.empty:
                # Берем первое найденное совпадение
                match_idx = matches.index[0]
                ma_value = float(matches.iloc[0][ma_column])
                ma_values.append(ma_value)
                used_indices.add(match_idx)
            else:
                # Если точного совпадения нет, пробуем приблизительное
                tolerance = 0.01  # Допуск для поиска
                approx_matches = df[
                    (abs(df["open"] - candle.open) < tolerance)
                    & (abs(df["high"] - candle.high) < tolerance)
                    & (abs(df["low"] - candle.low) < tolerance)
                    & (abs(df["close"] - candle.close) < tolerance)
                ]

                approx_matches = approx_matches[
                    ~approx_matches.index.isin(used_indices)
                ]

                if not approx_matches.empty:
                    match_idx = approx_matches.index[0]
                    ma_value = float(approx_matches.iloc[0][ma_column])
                    ma_values.append(ma_value)
                    used_indices.add(match_idx)
                else:
                    print(
                        f"Could not find MA value for candle: O={candle.open}, H={candle.high}, L={candle.low}, C={candle.close}"
                    )
                    return None

        return ma_values if len(ma_values) == 8 else None

    except Exception as e:
        print(f"Error extracting MA values: {e}")
        return None


def test_vectorization_pipeline(df: pd.DataFrame) -> None:
    """
    Тестирует полный пайплайн векторизации.
    """
    print("🧪 Testing vectorization pipeline...")

    try:
        # Получаем векторы
        pattern_vectors = get_pattern_vectors_with_ma(df)

        if not pattern_vectors:
            print("❌ No vectors generated")
            return

        # Анализируем результаты
        vectors = np.array([pv.vector for pv in pattern_vectors])

        print(f"✅ Generated {len(vectors)} vectors")
        print(f"Vector shape: {vectors.shape}")
        print(f"Vector range: [{vectors.min():.4f}, {vectors.max():.4f}]")
        print(
            f"MA parameters sample: {vectors[0, 40:44] if len(vectors) > 0 else 'None'}"
        )

        # Проверяем на NaN и Inf
        nan_count = np.isnan(vectors).sum()
        inf_count = np.isinf(vectors).sum()

        if nan_count > 0:
            print(f"⚠️  Found {nan_count} NaN values")
        if inf_count > 0:
            print(f"⚠️  Found {inf_count} Inf values")

        if nan_count == 0 and inf_count == 0:
            print("✅ All values are valid")

        print("🎯 Vectorization pipeline test completed!")

    except Exception as e:
        print(f"❌ Pipeline test failed: {e}")
        import traceback

        traceback.print_exc()
