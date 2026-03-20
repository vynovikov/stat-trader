from abc import ABC, abstractmethod
from typing import List

from domain.models.estimation import Estimation
from domain.types.candle import Candle
from domain.types.direction import Direction


class Estimator(ABC):
    @abstractmethod
    def estimate(
        self, candles: List[Candle], direction: Direction, from_candle_id: int
    ) -> Estimation: ...

    @abstractmethod
    def candles_num(self, candles: List[Candle]) -> int: ...
