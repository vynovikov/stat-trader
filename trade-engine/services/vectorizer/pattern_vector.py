from dataclasses import dataclass

import numpy as np

from domain.types.direction import Direction


@dataclass
class PatternVector:
    """
    Объединяет векторное представление паттерна с его направлением.
    Это позволяет держать связанные данные вместе и избежать
    случайного рассинхронизирования векторов и направлений.
    """

    vector: np.ndarray
    direction: Direction

    def to_scatter_direction(self) -> Direction:
        return Direction.UP if self.direction == Direction.UP else Direction.DOWN
