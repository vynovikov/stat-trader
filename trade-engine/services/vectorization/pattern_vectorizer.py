from typing import List, Optional, Tuple

import numpy as np
import pandas as pd

from domain.models.segment import Segment
from domain.types.candle import Candle
from services.vectorizer.pattern_vector import PatternVector


class PatternVectorizer:
    """
    Отвечает за векторизацию сегментов с добавлением контекстной информации.
    Следует принципу единственной ответственности.
    """

    def __init__(self, ma_short_col: str = "MA_50", ma_long_col: str = "MA_200"):
        """
        Initialize pattern vectorizer.

        Args:
            ma_short_col: Column name for short MA (default: MA_50)
            ma_long_col: Column name for long MA (default: MA_200)
        """
        self.ma_short_col = ma_short_col
        self.ma_long_col = ma_long_col

    def vectorize_segments(
        self, segments: List[Segment], df: pd.DataFrame
    ) -> List[PatternVector]:
        """
        Векторизует список сегментов с добавлением MA контекста.

        Args:
            segments: Список сегментов от Marker
            df: DataFrame с ценовыми данными и MA колонками

        Returns:
            Список PatternVector с 44-параметрическими векторами
        """
        result = []

        for segment in segments:
            if len(segment.Pre) == 8:  # Только полные прелюдии
                try:
                    # Извлекаем MA данные для сегмента
                    ma_short_values = self._extract_ma_for_segment(
                        df, segment, self.ma_short_col
                    )
                    ma_long_values = self._extract_ma_for_segment(
                        df, segment, self.ma_long_col
                    )

                    # Обновляем характеристики с MA данными
                    segment.update_pattern_characteristics(
                        ma_short_values, ma_long_values
                    )

                    # Получаем 44-параметрический вектор
                    vector = segment.get_pattern_vector()

                    # Создаем PatternVector
                    pattern_vector = PatternVector(
                        vector=vector, direction=segment.get_direction()
                    )
                    result.append(pattern_vector)

                except Exception as e:
                    print(f"Warning: Failed to vectorize segment - {e}")
                    continue

        return result

    def _extract_ma_for_segment(
        self, df: pd.DataFrame, segment: Segment, ma_column: str
    ) -> Optional[List[float]]:
        """
        Извлекает MA значения для свечей сегмента из DataFrame.

        Args:
            df: DataFrame с данными
            segment: Сегмент для которого нужны MA данные
            ma_column: Название колонки с MA

        Returns:
            Список MA значений для 8 свечей прелюдии или None
        """
        if ma_column not in df.columns:
            return None

        if len(segment.Pre) != 8:
            return None

        # Простая стратегия: ищем MA значения по индексам
        # В реальной системе может потребоваться более сложная логика сопоставления
        # основанная на timestamp или других идентификаторах

        try:
            ma_values = []

            # Для упрощения используем индексы - в реальной системе
            # нужно будет сопоставлять по timestamp
            for i, candle in enumerate(segment.Pre):
                # Здесь нужна логика поиска соответствующей строки в DataFrame
                # Пока используем упрощенный подход
                ma_value = self._find_ma_for_candle(df, candle, ma_column, i)
                if ma_value is not None:
                    ma_values.append(ma_value)
                else:
                    return None  # Если не можем найти MA для какой-то свечи

            return ma_values if len(ma_values) == 8 else None

        except Exception as e:
            print(f"Error extracting MA values: {e}")
            return None

    def _find_ma_for_candle(
        self, df: pd.DataFrame, candle: Candle, ma_column: str, index_hint: int
    ) -> Optional[float]:
        """
        Находит MA значение для конкретной свечи.

        Упрощенная реализация - в реальности нужно сопоставление по timestamp.
        """
        try:
            # Простая стратегия: используем приблизительное сопоставление
            # В реальной системе нужно сопоставлять по timestamp

            # Ищем строку с наиболее близкими OHLC значениями
            candidates = df[
                (abs(df["open"] - candle.open) < 0.01)
                & (abs(df["high"] - candle.high) < 0.01)
                & (abs(df["low"] - candle.low) < 0.01)
                & (abs(df["close"] - candle.close) < 0.01)
            ]

            if not candidates.empty:
                return float(candidates.iloc[0][ma_column])

            # Fallback: если точное сопоставление не найдено,
            # возвращаем среднее значение MA в окрестности
            start_idx = max(0, index_hint * 10)  # Приблизительная позиция
            end_idx = min(len(df), start_idx + 20)

            if start_idx < len(df):
                return float(df.iloc[start_idx:end_idx][ma_column].mean())

            return None

        except Exception:
            return None

    def validate_data(self, df: pd.DataFrame) -> bool:
        """
        Проверяет, что DataFrame содержит необходимые колонки.

        Args:
            df: DataFrame для проверки

        Returns:
            True если все необходимые колонки присутствуют
        """
        required_columns = ["open", "high", "low", "close", "volume"]
        optional_columns = [self.ma_short_col, self.ma_long_col]

        missing_required = [col for col in required_columns if col not in df.columns]
        missing_optional = [col for col in optional_columns if col not in df.columns]

        if missing_required:
            raise ValueError(f"Missing required columns: {missing_required}")

        if missing_optional:
            print(f"Warning: Missing optional MA columns: {missing_optional}")

        return True
