from dataclasses import dataclass, field
from typing import List


@dataclass
class PatternCharacteristics:
    """
    Характеристики прелюдии (8 свечей) для построения вектора.
    Всего 44 параметра: 24 (форма) + 8 (позиция) + 8 (объемы) + 4 (MA)
    """

    # === ФОРМА СВЕЧЕЙ (24 параметра) ===
    # Для каждой из 8 свечей: отношения размеров к полной длине свечи
    candles_num: int = 4
    body_ratios: List[float] = field(default_factory=list)  # 8 параметров
    upper_shadow_ratios: List[float] = field(default_factory=list)  # 8 параметров
    lower_shadow_ratios: List[float] = field(default_factory=list)  # 8 параметров

    # === ОТНОСИТЕЛЬНОЕ РАСПОЛОЖЕНИЕ (8 параметров) ===
    # Для каждой свечи: относительная позиция mid_price относительно первой свечи
    relative_positions: List[float] = field(default_factory=list)  # 8 параметров

    # === ОБЪЕМЫ (8 параметров) ===
    # Для каждой свечи: объем относительно среднего объема прелюдии
    relative_volumes: List[float] = field(default_factory=list)  # 8 параметров

    # === MA КОНТЕКСТ (4 параметра) ===
    # Позиция прелюдии относительно скользящих средних
    ma50_position: float = 0.0  # (close[0] - MA50[0]) / MA50[0]
    ma200_position: float = 0.0  # (close[0] - MA200[0]) / MA200[0]
    ma50_trend: float = 0.0  # (MA50[7] - MA50[0]) / MA50[0]
    ma200_trend: float = 0.0  # (MA200[7] - MA200[0]) / MA200[0]

    def get_vector_size(self) -> int:
        """Возвращает ожидаемый размер вектора (44)"""
        return self.candles_num * 5 + 4  # body + upper + lower + position + volume + ma

    def validate(self) -> bool:
        """Проверяет, что все списки содержат ровно 8 элементов"""
        return (
            len(self.body_ratios) == self.candles_num
            and len(self.upper_shadow_ratios) == self.candles_num
            and len(self.lower_shadow_ratios) == self.candles_num
            and len(self.relative_positions) == self.candles_num
            and len(self.relative_volumes) == self.candles_num
        )

    def clear(self):
        """Очищает все списки для пересчета"""
        self.body_ratios.clear()
        self.upper_shadow_ratios.clear()
        self.lower_shadow_ratios.clear()
        self.relative_positions.clear()
        self.relative_volumes.clear()
