from dataclasses import dataclass, field
from datetime import datetime, timedelta
from typing import List, Optional

import numpy as np

from domain.models.pattern_characteristics import PatternCharacteristics
from domain.models.trade_params import TradeParams
from domain.types.candle import Candle
from domain.types.category import Category
from domain.types.direction import Direction


@dataclass
class Segment:
    Pre: List[Candle] = field(default_factory=list)
    Trend: List[Candle] = field(default_factory=list)
    Params: TradeParams = field(default_factory=lambda: TradeParams())
    Pattern: PatternCharacteristics = field(
        default_factory=lambda: PatternCharacteristics()
    )

    def get_direction(self) -> Direction:
        return self.Params.direction

    def add_to_pre(self, *candles: Candle):
        """Add candles to prelude without automatic pattern characteristics update"""
        self.Pre.extend(candles)

    def add_to_trend(self, *candles: Candle):
        self.Trend.extend(candles)

    def direction(self) -> Direction:
        return self.Params.direction

    def category(self) -> Category:
        return self.Params.category

    def profit(self) -> float:
        return self.Params.profit

    def risk(self) -> float:
        return self.Params.risk

    def profit_risk_ratio(self) -> float:
        return self.Params.profit_risk_ratio

    def candles_num(self) -> int:
        return self.Params.candles_num

    def created_at(self) -> datetime:
        return self.Params.created_at

    def expire_at(self) -> datetime:
        return self.Params.expire_at

    def update_pattern_characteristics(
        self,
        candles_limit: int = 8,
        ma_50s: Optional[List[float]] = None,
        ma_200s: Optional[List[float]] = None,
    ):
        """Обновляет характеристики паттерна на основе 8 свечей прелюдии"""
        if not self.Pre or len(self.Pre) != candles_limit:
            return

        # Очищаем списки для нового расчета
        self.Pattern.clear()

        # Извлекаем данные свечей
        candles = self.Pre
        volumes = [c.volume for c in candles]
        avg_volume = sum(volumes) / len(volumes) if volumes else 1.0

        # Вычисляем общий диапазон прелюдии для нормализации позиций
        all_highs = [c.high for c in candles]
        all_lows = [c.low for c in candles]
        prelude_range = max(all_highs) - min(all_lows)
        first_mid_price = (candles[0].high + candles[0].low) / 2

        # === 1. ФОРМА СВЕЧЕЙ (24 параметра) ===
        for candle in candles:
            # Полная длина свечи
            full_length = candle.high - candle.low

            if full_length > 0:
                # Размер тела относительно полной длины
                body_size = abs(candle.close - candle.open)
                body_ratio = body_size / full_length

                # Размеры теней относительно полной длины
                upper_shadow = candle.high - max(candle.open, candle.close)
                lower_shadow = min(candle.open, candle.close) - candle.low
                upper_ratio = upper_shadow / full_length
                lower_ratio = lower_shadow / full_length
            else:
                # Вырожденный случай - свеча без диапазона
                body_ratio = upper_ratio = lower_ratio = 0.0

            self.Pattern.body_ratios.append(body_ratio)
            self.Pattern.upper_shadow_ratios.append(upper_ratio)
            self.Pattern.lower_shadow_ratios.append(lower_ratio)

        # === 2. ОТНОСИТЕЛЬНОЕ РАСПОЛОЖЕНИЕ (8 параметров) ===
        for candle in candles:
            mid_price = (candle.high + candle.low) / 2
            if prelude_range > 0:
                relative_pos = (mid_price - first_mid_price) / prelude_range
            else:
                relative_pos = 0.0
            self.Pattern.relative_positions.append(relative_pos)

        # === 3. ОБЪЕМЫ (8 параметров) ===
        for volume in volumes:
            if avg_volume > 0:
                rel_volume = volume / avg_volume
            else:
                rel_volume = 1.0
            self.Pattern.relative_volumes.append(rel_volume)

        # === 4. MA КОНТЕКСТ (4 параметра) ===
        if ma_50s and len(ma_50s) >= 8:
            first_close = candles[0].close
            if ma_50s[0] > 0:
                self.Pattern.ma50_position = (first_close - ma_50s[0]) / ma_50s[0]
            if ma_50s[0] > 0:
                self.Pattern.ma50_trend = (ma_50s[7] - ma_50s[0]) / ma_50s[0]

        if ma_200s and len(ma_200s) >= 8:
            first_close = candles[0].close
            if ma_200s[0] > 0:
                self.Pattern.ma200_position = (first_close - ma_200s[0]) / ma_200s[0]
            if ma_200s[0] > 0:
                self.Pattern.ma200_trend = (ma_200s[7] - ma_200s[0]) / ma_200s[0]

        self.Params.created_at = candles[-1].close_time
        self.Params.expire_at = candles[-1].close_time + timedelta(days=178)

    def get_pattern_vector(self) -> np.ndarray:
        """Преобразует характеристики паттерна в вектор из 44 элементов"""
        if not self.Pattern.validate():
            raise ValueError("Pattern characteristics not properly initialized")

        vector = []

        # Форма свечей (24 параметра)
        vector.extend(self.Pattern.body_ratios)  # 8 элементов
        vector.extend(self.Pattern.upper_shadow_ratios)  # 8 элементов
        vector.extend(self.Pattern.lower_shadow_ratios)  # 8 элементов

        # Относительное расположение (8 параметров)
        vector.extend(self.Pattern.relative_positions)  # 8 элементов

        # Объемы (8 параметров)
        vector.extend(self.Pattern.relative_volumes)  # 8 элементов

        # MA контекст (4 параметра)
        vector.extend(
            [
                self.Pattern.ma50_position,
                self.Pattern.ma200_position,
                self.Pattern.ma50_trend,
                self.Pattern.ma200_trend,
            ]
        )  # 4 элемента

        return np.array(vector)  # Итого: 44 элемента
